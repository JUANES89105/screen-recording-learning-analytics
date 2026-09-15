"""Reproduce the final study labels from privacy-safe refinement evidence."""

from __future__ import annotations

import argparse
import csv
import math
import unicodedata
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

from .config import load_site_config


FINAL_COLUMNS = [
    "video_id",
    "start_time_s",
    "end_time_s",
    "duration_s",
    "category",
    "classification_method",
    "ocr_mode",
    "temporal_interpolation",
    "manual_review",
]


def normalize_label(value: object) -> str:
    text = str(value or "").lower()
    text = unicodedata.normalize("NFKD", text)
    text = "".join(
        character
        for character in text
        if not unicodedata.combining(character)
    )
    return " ".join(text.split())


def parse_bool(value: object) -> bool:
    normalized = normalize_label(value)
    if normalized in {"1", "true", "yes"}:
        return True
    if normalized in {"0", "false", "no", ""}:
        return False
    raise ValueError(f"Invalid Boolean value: {value!r}")


def historical_category(label: str, categories: dict) -> str | None:
    normalized = normalize_label(label)
    for category, specification in categories.items():
        labels = [
            normalize_label(value)
            for value in (specification or {}).get(
                "historical_labels",
                [],
            )
        ]
        if normalized in labels:
            return category
    return None


def refine_privacy_safe_row(row: dict, config: dict) -> tuple[str, str, bool]:
    """Apply the historical refinement gates to redacted evidence flags."""
    categories = config["categories"]
    residual = config["residual_category"]
    refinement = config["refinement"]
    public = config["public_reproduction"]
    historical_column = config.get("historical_column", "palabra_base")
    historical = normalize_label(row[historical_column])
    base_category = historical_category(historical, categories)

    if base_category in refinement.get("preserve_historical", []):
        return base_category, "historical_base", False

    parent = refinement.get("historical_derived_rule", {}).get("category")
    if parent and base_category == parent:
        terms_column = public["matched_math_terms_column"]
        terms = row.get(terms_column, "").strip()
        if terms:
            derived = next(
                category
                for category, specification in categories.items()
                if (specification or {}).get("derived_from") == parent
            )
            method = (
                f"historical_{normalize_label(parent).replace(' ', '_')}"
                f" + math_terms: {terms}"
            )
            return derived, method, False
        method = (
            f"historical_{normalize_label(parent).replace(' ', '_')}"
            "_without_math_evidence"
        )
        return parent, method, False

    residual_labels = {
        normalize_label(value)
        for value in refinement.get("refine_residual_from", [])
    }
    if historical in residual_labels:
        evidence_columns = public["evidence_columns"]
        evidence_methods = public["evidence_methods"]
        review_categories = set(refinement.get("review_if_detected", []))

        for category in refinement.get("residual_priority", []):
            column = evidence_columns[category]
            if not parse_bool(row.get(column, "0")):
                continue
            if category in review_categories:
                return residual, evidence_methods[category], True
            return category, evidence_methods[category], False

        return residual, "residual", True

    mapping = refinement.get("historical_to_residual", {}).get(historical)
    if mapping:
        method = mapping.get("method", f"historical_{historical}")
        return (
            mapping.get("category", residual),
            method,
            bool(mapping.get("requires_review", True)),
        )

    if base_category:
        return base_category, "historical_base", False

    return residual, "unrecognized_historical_label", True


def build_candidate_episodes(rows: list[dict], gap_seconds: float) -> list[list[int]]:
    """Group review candidates separated by no more than the historical 3-s gap."""
    candidates = [
        index
        for index, row in enumerate(rows)
        if row["requires_review"]
    ]
    episodes: list[list[int]] = []
    current: list[int] = []
    previous_index: int | None = None

    for index in candidates:
        row = rows[index]
        starts_new = previous_index is None
        if previous_index is not None:
            previous = rows[previous_index]
            gap = float(row["start_time_s"]) - float(previous["end_time_s"])
            starts_new = (
                row["video_id"] != previous["video_id"]
                or gap > gap_seconds
            )

        if starts_new:
            if current:
                episodes.append(current)
            current = [index]
        else:
            current.append(index)
        previous_index = index

    if current:
        episodes.append(current)
    return episodes


def reproduce_rows(
    input_rows: list[dict],
    manual_decisions: list[dict],
    config: dict,
) -> tuple[list[dict], dict]:
    public = config["public_reproduction"]
    expected_columns = {
        "segment_id",
        "video_id",
        "start_time_s",
        "end_time_s",
        "duration_s",
        "palabra_base",
        "ocr_mode",
        public["matched_math_terms_column"],
        *public["evidence_columns"].values(),
    }
    if not input_rows:
        raise ValueError("The public refinement input is empty.")
    missing = expected_columns.difference(input_rows[0])
    if missing:
        raise ValueError(f"Missing public refinement columns: {sorted(missing)}")

    segment_ids = [row["segment_id"] for row in input_rows]
    if len(segment_ids) != len(set(segment_ids)):
        raise ValueError("segment_id values must be unique.")

    rows: list[dict] = []
    for source in input_rows:
        start = float(source["start_time_s"])
        end = float(source["end_time_s"])
        duration = float(source["duration_s"])
        if not all(math.isfinite(value) for value in (start, end, duration)):
            raise ValueError(f"Non-finite time in {source['segment_id']}")
        if end < start or duration < 0:
            raise ValueError(f"Invalid time interval in {source['segment_id']}")

        category, method, requires_review = refine_privacy_safe_row(
            source,
            config,
        )
        rows.append(
            {
                **source,
                "automatic_category": category,
                "automatic_method": method,
                "requires_review": requires_review,
                "category": category,
                "classification_method": method,
                "temporal_interpolation": False,
                "manual_review": False,
            }
        )

    episodes = build_candidate_episodes(
        rows,
        float(public["episode_gap_seconds"]),
    )
    temporal_limit = float(public["temporal_max_duration_seconds"])
    unresolved: list[list[int]] = []
    resolved_episodes = 0
    resolved_segments = 0

    for episode in episodes:
        first = episode[0]
        last = episode[-1]
        video_id = rows[first]["video_id"]
        previous_category = ""
        following_category = ""
        if first > 0 and rows[first - 1]["video_id"] == video_id:
            previous_category = rows[first - 1]["automatic_category"]
        if last + 1 < len(rows) and rows[last + 1]["video_id"] == video_id:
            following_category = rows[last + 1]["automatic_category"]
        duration = (
            float(rows[last]["end_time_s"])
            - float(rows[first]["start_time_s"])
        )

        if (
            previous_category
            and previous_category == following_category
            and duration <= temporal_limit
        ):
            resolved_episodes += 1
            resolved_segments += len(episode)
            method = (
                "temporal_interpolation_30s_between_"
                + previous_category
            )
            for index in episode:
                rows[index]["category"] = previous_category
                rows[index]["classification_method"] = method
                rows[index]["temporal_interpolation"] = True
                rows[index]["requires_review"] = False
        else:
            unresolved.append(episode)

    decisions: dict[tuple[str, int], dict] = {}
    for decision in manual_decisions:
        key = (decision["video_id"], int(decision["episode_id"]))
        if key in decisions:
            raise ValueError(f"Duplicate manual decision: {key}")
        decisions[key] = decision

    episode_number_by_video: Counter = Counter()
    used_decisions: set[tuple[str, int]] = set()
    manual_segments = 0
    for episode in unresolved:
        first = episode[0]
        last = episode[-1]
        video_id = rows[first]["video_id"]
        episode_number_by_video[video_id] += 1
        key = (video_id, episode_number_by_video[video_id])
        if key not in decisions:
            raise ValueError(f"Missing manual decision for {key}")
        decision = decisions[key]

        expected = (
            float(rows[first]["start_time_s"]),
            float(rows[last]["end_time_s"]),
            len(episode),
        )
        observed = (
            float(decision["start_time_s"]),
            float(decision["end_time_s"]),
            int(decision["n_segments"]),
        )
        if (
            abs(expected[0] - observed[0]) > 1e-6
            or abs(expected[1] - observed[1]) > 1e-6
            or expected[2] != observed[2]
        ):
            raise ValueError(
                f"Manual decision boundaries do not match episode {key}: "
                f"expected {expected}, found {observed}"
            )

        category = decision["category"]
        if category not in config["categories"]:
            raise ValueError(f"Unknown manual category {category!r} for {key}")
        used_decisions.add(key)
        manual_segments += len(episode)
        for index in episode:
            rows[index]["category"] = category
            rows[index]["classification_method"] = "manual_episode_review"
            rows[index]["manual_review"] = True
            rows[index]["requires_review"] = False

    unused = set(decisions).difference(used_decisions)
    if unused:
        raise ValueError(f"Unused manual decisions: {sorted(unused)[:10]}")

    output = [
        {
            "video_id": row["video_id"],
            "start_time_s": row["start_time_s"],
            "end_time_s": row["end_time_s"],
            "duration_s": row["duration_s"],
            "category": row["category"],
            "classification_method": row["classification_method"],
            "ocr_mode": row["ocr_mode"],
            "temporal_interpolation": str(row["temporal_interpolation"]),
            "manual_review": str(row["manual_review"]),
        }
        for row in rows
    ]
    audit = {
        "records": len(rows),
        "candidate_episodes": len(episodes),
        "candidate_segments": sum(len(episode) for episode in episodes),
        "temporally_resolved_episodes": resolved_episodes,
        "temporally_resolved_segments": resolved_segments,
        "manual_episodes": len(unresolved),
        "manual_segments": manual_segments,
    }
    return output, audit


def read_csv(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FINAL_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)


def summarize(rows: list[dict]) -> dict:
    counts = Counter(row["category"] for row in rows)
    durations: defaultdict[str, Decimal] = defaultdict(Decimal)
    for row in rows:
        durations[row["category"]] += Decimal(row["duration_s"])

    transitions = 0
    previous: dict | None = None
    for row in rows:
        if (
            previous is not None
            and row["video_id"] == previous["video_id"]
            and row["category"] != previous["category"]
        ):
            transitions += 1
        previous = row

    return {
        "counts": counts,
        "durations": durations,
        "total_duration": sum(durations.values(), Decimal("0")),
        "transitions": transitions,
    }


def verify_rows(reproduced: list[dict], authoritative: list[dict]) -> dict:
    if len(reproduced) != len(authoritative):
        raise ValueError(
            f"Row-count mismatch: {len(reproduced)} != {len(authoritative)}"
        )
    key_columns = ["video_id", "start_time_s", "end_time_s", "duration_s"]
    key_matches = 0
    label_matches = 0
    method_matches = 0
    flag_matches = 0
    for produced, expected in zip(reproduced, authoritative):
        if all(produced[column] == expected[column] for column in key_columns):
            key_matches += 1
        if produced["category"] == expected["category"]:
            label_matches += 1
        if produced["classification_method"] == expected["classification_method"]:
            method_matches += 1
        if (
            produced["temporal_interpolation"]
            == expected["temporal_interpolation"]
            and produced["manual_review"] == expected["manual_review"]
        ):
            flag_matches += 1
    return {
        "key_matches": key_matches,
        "label_matches": label_matches,
        "method_matches": method_matches,
        "flag_matches": flag_matches,
        "records": len(reproduced),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Reproduce the authoritative final nine-category classification "
            "from privacy-safe historical refinement evidence."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/refinement_input_public.csv"),
    )
    parser.add_argument(
        "--manual-decisions",
        type=Path,
        default=Path("data/processed/manual_review_decisions_public.csv"),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config/sites.yaml"),
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--verify-against",
        type=Path,
        default=Path("data/processed/corpus_100_videos_public_final.csv"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_site_config(args.config)
    rows, audit = reproduce_rows(
        read_csv(args.input),
        read_csv(args.manual_decisions),
        config,
    )
    write_csv(args.output, rows)
    summary = summarize(rows)
    verification = verify_rows(rows, read_csv(args.verify_against))

    print("REPRODUCTION AUDIT")
    for key, value in audit.items():
        print(f"{key}: {value}")
    print(f"label_agreement: {verification['label_matches']}/{verification['records']}")
    print(f"method_agreement: {verification['method_matches']}/{verification['records']}")
    print(f"flag_agreement: {verification['flag_matches']}/{verification['records']}")
    print(f"total_duration_s: {summary['total_duration']}")
    print(f"transitions: {summary['transitions']}")
    print("category_counts:")
    for category in config["categories"]:
        print(f"  {category}: {summary['counts'][category]}")
    print("category_durations_s:")
    for category in config["categories"]:
        print(f"  {category}: {summary['durations'][category]}")

    if any(
        verification[key] != verification["records"]
        for key in ("key_matches", "label_matches", "method_matches", "flag_matches")
    ):
        raise SystemExit("Reproduced output does not match the authoritative dataset.")


if __name__ == "__main__":
    main()
