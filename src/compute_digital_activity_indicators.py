"""Compute the study's descriptive digital-activity indicators."""

from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path


REQUIRED_COLUMNS = {
    "video_id",
    "start_time_s",
    "end_time_s",
    "duration_s",
    "category",
}


def read_segments(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise ValueError("The segment dataset has no header.")
        missing = REQUIRED_COLUMNS.difference(reader.fieldnames)
        if missing:
            raise ValueError(f"Missing segment columns: {sorted(missing)}")
        rows = list(reader)
    if not rows:
        raise ValueError("The segment dataset is empty.")
    return rows


def _median(values: list[int]) -> Decimal:
    ordered = sorted(values)
    middle = len(ordered) // 2
    if len(ordered) % 2:
        return Decimal(ordered[middle])
    return Decimal(ordered[middle - 1] + ordered[middle]) / Decimal(2)


def compute_indicators(rows: list[dict[str, str]]) -> dict:
    category_counts: Counter[str] = Counter()
    category_durations: defaultdict[str, Decimal] = defaultdict(Decimal)
    videos: defaultdict[str, list[tuple[int, dict[str, str]]]] = defaultdict(list)

    for index, row in enumerate(rows):
        duration = Decimal(row["duration_s"])
        start = Decimal(row["start_time_s"])
        end = Decimal(row["end_time_s"])
        if duration < 0 or end < start:
            raise ValueError(f"Invalid interval at input row {index + 2}.")
        category_counts[row["category"]] += 1
        category_durations[row["category"]] += duration
        videos[row["video_id"]].append((index, row))

    total_segments = len(rows)
    total_duration = sum(category_durations.values(), Decimal(0))
    category_summary = []
    for category, count in sorted(
        category_counts.items(),
        key=lambda item: (-item[1], item[0]),
    ):
        duration = category_durations[category]
        category_summary.append(
            {
                "category": category,
                "segments": count,
                "duration_s": duration,
                "percent_segments": (
                    Decimal(count) * Decimal(100) / Decimal(total_segments)
                ),
                "duration_h": duration / Decimal(3600),
                "percent_time": duration * Decimal(100) / total_duration,
            }
        )

    transitions_per_video = []
    transition_pairs: Counter[tuple[str, str]] = Counter()
    for video_id in sorted(videos):
        ordered = sorted(
            videos[video_id],
            key=lambda item: (
                Decimal(item[1]["start_time_s"]),
                Decimal(item[1]["end_time_s"]),
                item[0],
            ),
        )
        transition_count = 0
        for (_, previous), (_, current) in zip(ordered, ordered[1:]):
            source = previous["category"]
            target = current["category"]
            if source != target:
                transition_count += 1
                transition_pairs[(source, target)] += 1
        transitions_per_video.append(
            {"video_id": video_id, "transitions": transition_count}
        )

    transition_values = [row["transitions"] for row in transitions_per_video]
    total_transitions = sum(transition_values)
    mean_transitions = Decimal(total_transitions) / Decimal(len(transition_values))
    if len(transition_values) > 1:
        variance = sum(
            (Decimal(value) - mean_transitions) ** 2
            for value in transition_values
        ) / Decimal(len(transition_values) - 1)
        standard_deviation = variance.sqrt()
    else:
        standard_deviation = Decimal(0)

    ranked_pairs = [
        {"from_category": source, "to_category": target, "count": count}
        for (source, target), count in sorted(
            transition_pairs.items(),
            key=lambda item: (-item[1], item[0][0], item[0][1]),
        )
    ]

    categories = sorted(category_counts)
    transition_matrix = []
    for source in categories:
        transition_matrix.append(
            {
                "from_category": source,
                **{
                    target: transition_pairs[(source, target)]
                    for target in categories
                },
            }
        )

    return {
        "category_summary": category_summary,
        "transitions_per_video": transitions_per_video,
        "ranked_transition_pairs": ranked_pairs,
        "transition_matrix": transition_matrix,
        "matrix_categories": categories,
        "overall": {
            "videos": len(videos),
            "segments": total_segments,
            "total_duration_s": total_duration,
            "total_duration_h": total_duration / Decimal(3600),
            "total_transitions": total_transitions,
            "mean_transitions_per_video": mean_transitions,
            "median_transitions_per_video": _median(transition_values),
            "minimum_transitions_per_video": min(transition_values),
            "maximum_transitions_per_video": max(transition_values),
            "sample_sd_transitions_per_video": standard_deviation,
        },
    }


def _serializable(value: object) -> object:
    if isinstance(value, Decimal):
        return format(value, "f")
    return value


def _write_csv(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(
            {
                key: _serializable(value)
                for key, value in row.items()
            }
            for row in rows
        )


def write_indicators(indicators: dict, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "category": output_dir / "digital_activity_category_summary.csv",
        "per_video": output_dir / "transitions_per_video.csv",
        "ranked": output_dir / "category_transitions_ranked.csv",
        "matrix": output_dir / "category_transition_matrix.csv",
        "overall": output_dir / "digital_activity_overall_summary.csv",
    }
    _write_csv(
        paths["category"],
        [
            "category",
            "segments",
            "duration_s",
            "percent_segments",
            "duration_h",
            "percent_time",
        ],
        indicators["category_summary"],
    )
    _write_csv(
        paths["per_video"],
        ["video_id", "transitions"],
        indicators["transitions_per_video"],
    )
    _write_csv(
        paths["ranked"],
        ["from_category", "to_category", "count"],
        indicators["ranked_transition_pairs"],
    )
    _write_csv(
        paths["matrix"],
        ["from_category", *indicators["matrix_categories"]],
        indicators["transition_matrix"],
    )
    overall_rows = [
        {"metric": metric, "value": value}
        for metric, value in indicators["overall"].items()
    ]
    _write_csv(paths["overall"], ["metric", "value"], overall_rows)
    return list(paths.values())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Derive category and transition indicators from the authoritative "
            "public segment dataset."
        )
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/processed/corpus_100_videos_public_final.csv"),
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    indicators = compute_indicators(read_segments(args.input))
    paths = write_indicators(indicators, args.output_dir)
    overall = indicators["overall"]

    print("DIGITAL ACTIVITY INDICATORS")
    for metric, value in overall.items():
        print(f"{metric}: {_serializable(value)}")
    print("category_summary:")
    for row in indicators["category_summary"]:
        print(
            f"  {row['category']}: {row['segments']} segments, "
            f"{row['duration_s']} seconds"
        )
    print("outputs:")
    for path in paths:
        print(f"  {path}")


if __name__ == "__main__":
    main()
