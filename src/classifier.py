from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import load_site_config
from .text_utils import normalize_text


@dataclass(frozen=True)
class Classification:
    category: str
    matched_pattern: str | None
    technical_markers: tuple[str, ...]
    score: float


def count_occurrences(text: str, pattern: str) -> int:
    """
    Count occurrences of a normalized pattern in normalized OCR text.
    """
    pattern = normalize_text(pattern)

    if not pattern:
        return 0

    return text.count(pattern)


class RuleBasedClassifier:
    """
    Deterministic classifier driven entirely by an external YAML file.

    Classification is based on accumulated weighted evidence:
    - strong_patterns receive a high weight
    - regular patterns receive a lower weight

    The category with the highest total score is selected.
    """

    def __init__(self, config_path: str | Path):
        self.config = load_site_config(config_path)

        self.text_column = self.config["text_column"]
        self.residual_category = self.config["residual_category"]
        self.categories = self.config["categories"]
        self.technical_markers = self.config.get("technical_markers", {})

        scoring = self.config.get("scoring", {})

        self.strong_weight = scoring.get("strong_weight", 10)
        self.pattern_weight = scoring.get("pattern_weight", 1)
        self.minimum_score = scoring.get("minimum_score", 1)

    def classify_text(self, text) -> Classification:
        normalized = normalize_text(text)

        scores = {}
        matched_patterns = {}

        # ----------------------------------------------------
        # CALCULATE EVIDENCE SCORE FOR EACH CATEGORY
        # ----------------------------------------------------

        for category, spec in self.categories.items():

            score = 0
            evidence = []

            # Strong evidence
            for pattern in spec.get("strong_patterns", []):
                n = count_occurrences(normalized, pattern)

                if n > 0:
                    score += n * self.strong_weight
                    evidence.append(
                        f"{pattern} x{n} (strong)"
                    )

            # Normal evidence
            for pattern in spec.get("patterns", []):
                n = count_occurrences(normalized, pattern)

                if n > 0:
                    score += n * self.pattern_weight
                    evidence.append(
                        f"{pattern} x{n}"
                    )

            scores[category] = score
            matched_patterns[category] = evidence

        # ----------------------------------------------------
        # CHOOSE CATEGORY WITH MAXIMUM EVIDENCE
        # ----------------------------------------------------

        max_score = max(scores.values(), default=0)

        if max_score < self.minimum_score:
            category = self.residual_category
            matched_pattern = None
        else:
            candidates = [
                category
                for category, score in scores.items()
                if score == max_score
            ]

            # In a tie, preserve YAML order.
            category = candidates[0]

            matched_pattern = "; ".join(
                matched_patterns[category]
            )

        # ----------------------------------------------------
        # TECHNICAL MARKERS
        # ----------------------------------------------------

        markers = []

        for name, spec in self.technical_markers.items():

            detected = False

            for pattern in spec.get("patterns", []):
                if count_occurrences(normalized, pattern) > 0:
                    detected = True
                    break

            if detected:
                markers.append(name)

        return Classification(
            category=category,
            matched_pattern=matched_pattern,
            technical_markers=tuple(markers),
            score=max_score,
        )

    def classify_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:

        if self.text_column not in df.columns:
            raise ValueError(
                f"Required OCR column '{self.text_column}' was not found. "
                f"Available columns: {list(df.columns)}"
            )

        out = df.copy()

        results = out[self.text_column].apply(
            self.classify_text
        )

        out["categoria_automatica"] = results.map(
            lambda x: x.category
        )

        out["regla_detectada"] = results.map(
            lambda x: x.matched_pattern or ""
        )

        out["puntaje_clasificacion"] = results.map(
            lambda x: x.score
        )

        out["marcas_tecnicas"] = results.map(
            lambda x: "; ".join(x.technical_markers)
        )

        out["requiere_revision"] = (
            out["categoria_automatica"]
            .eq(self.residual_category)
        )

        return out


def classify_excel(
    input_path: str | Path,
    config_path: str | Path,
    output_dir: str | Path,
):
    from .reporting import export_results

    input_path = Path(input_path)

    df = pd.read_excel(input_path)

    classifier = RuleBasedClassifier(config_path)

    classified = classifier.classify_dataframe(df)

    return export_results(
        classified,
        output_dir
    )
