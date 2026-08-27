from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .config import load_site_config
from .text_utils import normalize_text


# ============================================================
# HELPERS
# ============================================================

def contains_any(text: str, patterns: list[str]) -> list[str]:
    """
    Return all normalized patterns found in normalized text.
    """
    hits = []

    for pattern in patterns:
        normalized_pattern = normalize_text(pattern)

        if (
            normalized_pattern
            and normalized_pattern in text
        ):
            hits.append(pattern)

    return hits


def category_for_historical_label(
    historical: str,
    categories: dict,
) -> str | None:
    """
    Find the category associated with a historical label.
    """
    for category, spec in categories.items():

        spec = spec or {}

        historical_labels = [
            normalize_text(x)
            for x in spec.get(
                "historical_labels",
                []
            )
        ]

        if historical in historical_labels:
            return category

    return None


def derived_category_for_parent(
    parent_category: str,
    text: str,
    categories: dict,
) -> tuple[str | None, list[str]]:
    """
    Evaluate YAML-defined derived categories for a parent category.

    Currently supports:
        derivation.type = term_evidence
    """
    for category, spec in categories.items():

        spec = spec or {}

        if spec.get("derived_from") != parent_category:
            continue

        derivation = spec.get(
            "derivation",
            {}
        )

        derivation_type = derivation.get(
            "type"
        )

        if derivation_type == "term_evidence":

            terms = derivation.get(
                "terms",
                []
            )

            hits = contains_any(
                text,
                terms,
            )

            if hits:
                return category, hits

        else:
            raise ValueError(
                f"Unsupported derivation type "
                f"'{derivation_type}' "
                f"for category '{category}'."
            )

    return None, []


def strong_evidence_for_category(
    category: str,
    text: str,
    categories: dict,
) -> list[str]:
    """
    Return strong OCR evidence for a category.
    """
    spec = categories.get(
        category,
        {},
    ) or {}

    patterns = spec.get(
        "strong_patterns",
        [],
    )

    return contains_any(
        text,
        patterns,
    )


# ============================================================
# REFINEMENT ENGINE
# ============================================================

def refine_row(
    row: pd.Series,
    config: dict,
):
    """
    Apply the YAML-defined historical refinement rules.

    Returns:
        category
        evidence
        requires_manual_review
        review_reason
    """

    categories = config["categories"]
    residual = config["residual_category"]

    refinement = config.get(
        "refinement",
        {},
    )

    text = row["_normalized_text"]

    historical_column = config.get(
        "historical_column",
        "palabra_base",
    )

    historical = normalize_text(
        row.get(
            historical_column,
            "",
        )
    )

    # --------------------------------------------------------
    # 1. HISTORICAL LABEL -> CONFIGURED CATEGORY
    # --------------------------------------------------------

    historical_category = (
        category_for_historical_label(
            historical,
            categories,
        )
    )

    preserve_historical = refinement.get(
        "preserve_historical",
        [],
    )

    if (
        historical_category
        and historical_category
        in preserve_historical
    ):
        return (
            historical_category,
            "historical_base",
            False,
            "",
        )

    # --------------------------------------------------------
    # 2. HISTORICAL CATEGORY WITH DERIVED SUBCATEGORY
    # --------------------------------------------------------

    derived_rule = refinement.get(
        "historical_derived_rule",
        {}
    )

    parent_category = derived_rule.get(
        "category"
    )

    if (
        parent_category
        and historical_category == parent_category
    ):

        derived_category, hits = (
            derived_category_for_parent(
                parent_category,
                text,
                categories,
            )
        )

        if derived_category:
            return (
                derived_category,
                "historical_parent + derived_terms: "
                + "; ".join(hits[:10]),
                False,
                "",
            )

        return (
            parent_category,
            "historical_parent_without_derived_evidence",
            False,
            "",
        )

    # --------------------------------------------------------
    # 3. REFINE RESIDUAL HISTORICAL LABEL
    # --------------------------------------------------------

    refine_residual_from = [
        normalize_text(x)
        for x in refinement.get(
            "refine_residual_from",
            [],
        )
    ]

    if historical in refine_residual_from:

        residual_priority = refinement.get(
            "residual_priority",
            [],
        )

        review_if_detected = set(
            refinement.get(
                "review_if_detected",
                [],
            )
        )

        for category in residual_priority:

            hits = strong_evidence_for_category(
                category,
                text,
                categories,
            )

            if not hits:
                continue

            if category in review_if_detected:
                return (
                    residual,
                    "possible_"
                    + normalize_text(category)
                    .replace(" ", "_"),
                    True,
                    (
                        f"{category} detected in new OCR "
                        f"inside a historically residual segment"
                    ),
                )

            return (
                category,
                "strong_evidence: "
                + "; ".join(hits[:10]),
                False,
                "",
            )

        return (
            residual,
            "residual",
            True,
            "No strong evidence for configured refined categories",
        )

    # --------------------------------------------------------
    # 4. EXPLICIT HISTORICAL -> RESIDUAL MAPPINGS
    # --------------------------------------------------------

    historical_to_residual = refinement.get(
        "historical_to_residual",
        {},
    )

    mapping = historical_to_residual.get(
        historical
    )

    if mapping:

        return (
            mapping.get(
                "category",
                residual,
            ),
            "historical_to_residual",
            bool(
                mapping.get(
                    "requires_review",
                    True,
                )
            ),
            str(
                mapping.get(
                    "reason",
                    "",
                )
            ).strip(),
        )

    # --------------------------------------------------------
    # 5. OTHER HISTORICAL LABELS CONFIGURED IN YAML
    # --------------------------------------------------------

    if historical_category:

        return (
            historical_category,
            "historical_base",
            False,
            "",
        )

    # --------------------------------------------------------
    # 6. UNEXPECTED HISTORICAL LABEL
    # --------------------------------------------------------

    return (
        residual,
        "unrecognized_historical_label",
        True,
        (
            "Unrecognized historical label: "
            f"{historical}"
        ),
    )


# ============================================================
# SUMMARY
# ============================================================

def build_summary(
    df: pd.DataFrame,
) -> pd.DataFrame:

    summary = (
        df["categoria_refinada_auto"]
        .value_counts()
        .rename_axis("categoria")
        .reset_index(name="n")
    )

    summary["porcentaje"] = (
        summary["n"]
        / len(df)
        * 100
    ).round(2)

    if "Tiempo en página (s)" in df.columns:

        times = (
            df.groupby(
                "categoria_refinada_auto"
            )["Tiempo en página (s)"]
            .sum()
        )

        summary["tiempo_s"] = (
            summary["categoria"]
            .map(times)
        )

        summary["tiempo_h"] = (
            summary["tiempo_s"]
            / 3600
        ).round(4)

    return summary


# ============================================================
# CLI
# ============================================================

def parse_args():

    parser = argparse.ArgumentParser(
        description=(
            "Refine historical screen-recording "
            "classifications using a YAML configuration."
        )
    )

    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="Input Excel with historical labels and OCR text.",
    )

    parser.add_argument(
        "--config",
        type=Path,
        default=Path(
            "config/sites.yaml"
        ),
        help="Classification YAML configuration.",
    )

    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Directory for refinement outputs.",
    )

    return parser.parse_args()


# ============================================================
# MAIN
# ============================================================

def main():

    args = parse_args()

    config = load_site_config(
        args.config
    )

    categories = config["categories"]
    residual = config["residual_category"]

    text_column = config["text_column"]

    historical_column = config.get(
        "historical_column",
        "palabra_base",
    )

    print("=" * 100)
    print("CLASSIFICATION REFINEMENT")
    print("=" * 100)

    print("\nInput:")
    print(args.input)

    print("\nConfiguration:")
    print(args.config)

    df = pd.read_excel(
        args.input
    )

    print("\nRows:", len(df))

    if "video_id" in df.columns:
        print(
            "Videos:",
            df["video_id"].nunique(),
        )

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    required = [
        historical_column,
        text_column,
    ]

    if "video_id" in df.columns:
        required.append(
            "video_id"
        )

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Missing required columns: "
            + ", ".join(missing)
        )

    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    df["_normalized_text"] = (
        df[text_column]
        .apply(normalize_text)
    )

    # --------------------------------------------------------
    # REFINEMENT
    # --------------------------------------------------------

    results = df.apply(
        lambda row: refine_row(
            row,
            config,
        ),
        axis=1,
        result_type="expand",
    )

    results.columns = [
        "categoria_refinada_auto",
        "evidencia_refinamiento",
        "requiere_revision_manual",
        "motivo_revision",
    ]

    df = pd.concat(
        [
            df,
            results,
        ],
        axis=1,
    )

    # --------------------------------------------------------
    # CATEGORY CONTROL
    # --------------------------------------------------------

    configured_categories = set(
        categories
    )

    unexpected = sorted(
        set(
            df[
                "categoria_refinada_auto"
            ]
            .dropna()
            .unique()
        )
        - configured_categories
    )

    if unexpected:
        raise ValueError(
            "Unexpected categories generated: "
            + str(unexpected)
        )

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    summary = build_summary(
        df
    )

    review = df[
        df["requiere_revision_manual"]
    ].copy()

    # --------------------------------------------------------
    # CLEAN AUXILIARY COLUMN
    # --------------------------------------------------------

    df.drop(
        columns=[
            "_normalized_text"
        ],
        inplace=True,
    )

    review.drop(
        columns=[
            "_normalized_text"
        ],
        inplace=True,
        errors="ignore",
    )

    # --------------------------------------------------------
    # EXPORT
    # --------------------------------------------------------

    args.output_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        args.output_dir
        / "classification_refined.xlsx"
    )

    review_file = (
        args.output_dir
        / "manual_review.xlsx"
    )

    summary_file = (
        args.output_dir
        / "category_summary.xlsx"
    )

    df.to_excel(
        output_file,
        index=False,
    )

    review.to_excel(
        review_file,
        index=False,
    )

    summary.to_excel(
        summary_file,
        index=False,
    )

    # --------------------------------------------------------
    # REPORT
    # --------------------------------------------------------

    print("\n" + "=" * 100)
    print("DISTRIBUTION")
    print("=" * 100)

    print(
        summary.to_string(
            index=False
        )
    )

    print("\n" + "=" * 100)
    print("MANUAL REVIEW")
    print("=" * 100)

    print(
        "Segments requiring review:",
        len(review),
    )

    print(
        "Percentage:",
        f"{len(review)/len(df)*100:.2f}%",
    )

    if (
        "video_id" in review.columns
        and len(review)
    ):
        print(
            "Videos involved:",
            review[
                "video_id"
            ].nunique(),
        )

    if len(review):

        print("\nReasons:")

        print(
            review[
                "motivo_revision"
            ]
            .value_counts()
            .to_string()
        )

    # --------------------------------------------------------
    # STUDY-SPECIFIC REPRODUCTION CONTROLS
    # --------------------------------------------------------

    study = config.get(
        "study",
        {},
    )

    print("\n" + "=" * 100)
    print("REPRODUCTION CONTROLS")
    print("=" * 100)

    expected_segments = study.get(
        "expected_segments"
    )

    if expected_segments is not None:

        print(
            f"Expected segments "
            f"({expected_segments}):",
            len(df) == expected_segments,
        )

    expected_videos = study.get(
        "expected_videos"
    )

    if (
        expected_videos is not None
        and "video_id" in df.columns
    ):

        print(
            f"Expected videos "
            f"({expected_videos}):",
            (
                df["video_id"].nunique()
                == expected_videos
            ),
        )

    print(
        "Configured categories:",
        list(categories),
    )

    print(
        "Residual category:",
        residual,
    )

    print("\n" + "=" * 100)
    print("FILES")
    print("=" * 100)

    print(output_file)
    print(review_file)
    print(summary_file)


if __name__ == "__main__":
    main()
