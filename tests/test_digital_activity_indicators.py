from decimal import Decimal
from pathlib import Path

from src.compute_digital_activity_indicators import (
    compute_indicators,
    read_segments,
    write_indicators,
)


ROOT = Path(__file__).resolve().parents[1]


def test_authoritative_digital_activity_indicators(tmp_path):
    indicators = compute_indicators(
        read_segments(
            ROOT / "data" / "processed" / "corpus_100_videos_public_final.csv"
        )
    )
    overall = indicators["overall"]

    assert overall["videos"] == 100
    assert overall["segments"] == 18829
    assert overall["total_duration_s"] == Decimal("307976.40")
    assert overall["total_duration_h"].quantize(Decimal("0.01")) == Decimal("85.55")
    assert overall["total_transitions"] == 1482
    assert overall["mean_transitions_per_video"] == Decimal("14.82")
    assert overall["median_transitions_per_video"] == Decimal("4")
    assert overall["minimum_transitions_per_video"] == 0
    assert overall["maximum_transitions_per_video"] == 166
    assert overall["sample_sd_transitions_per_video"].quantize(
        Decimal("0.01")
    ) == Decimal("27.86")

    categories = {
        row["category"]: (row["segments"], row["duration_s"])
        for row in indicators["category_summary"]
    }
    assert categories == {
        "Quinan": (13707, Decimal("253043.65")),
        "YouTube": (1599, Decimal("2959.37")),
        "Juegos": (971, Decimal("5291.72")),
        "Wikipedia": (722, Decimal("1514.65")),
        "Google": (508, Decimal("4185.48")),
        "Google (Mat)": (427, Decimal("4360.81")),
        "Screen Recorder": (362, Decimal("23488.75")),
        "GeoGebra": (272, Decimal("2541.14")),
        "Otro sitio": (261, Decimal("10590.83")),
    }
    percentages = {
        row["category"]: (
            row["percent_segments"].quantize(Decimal("0.01")),
            row["percent_time"].quantize(Decimal("0.01")),
        )
        for row in indicators["category_summary"]
    }
    assert percentages == {
        "Quinan": (Decimal("72.80"), Decimal("82.16")),
        "YouTube": (Decimal("8.49"), Decimal("0.96")),
        "Juegos": (Decimal("5.16"), Decimal("1.72")),
        "Wikipedia": (Decimal("3.83"), Decimal("0.49")),
        "Google": (Decimal("2.70"), Decimal("1.36")),
        "Google (Mat)": (Decimal("2.27"), Decimal("1.42")),
        "Screen Recorder": (Decimal("1.92"), Decimal("7.63")),
        "GeoGebra": (Decimal("1.44"), Decimal("0.83")),
        "Otro sitio": (Decimal("1.39"), Decimal("3.44")),
    }

    pairs = {
        (row["from_category"], row["to_category"]): row["count"]
        for row in indicators["ranked_transition_pairs"]
    }
    assert pairs[("Quinan", "Screen Recorder")] == 154
    assert pairs[("Screen Recorder", "Quinan")] == 147
    assert pairs[("Quinan", "Google")] == 79
    assert pairs[("Quinan", "GeoGebra")] == 75
    assert pairs[("GeoGebra", "Quinan")] == 73
    assert pairs[("Juegos", "Quinan")] == 72
    assert pairs[("Quinan", "Juegos")] == 68
    assert pairs[("Quinan", "Google (Mat)")] == 65
    assert pairs[("Google (Mat)", "Quinan")] == 65
    assert pairs[("Google", "Google (Mat)")] == 42
    assert pairs[("Google (Mat)", "Google")] == 33
    assert pairs[("Otro sitio", "Google")] == 24
    assert pairs[("Google", "YouTube")] == 22
    assert pairs[("Google", "Otro sitio")] == 20
    assert pairs[("Google (Mat)", "GeoGebra")] == 19

    paths = write_indicators(indicators, tmp_path)
    assert len(paths) == 5
    assert all(path.is_file() for path in paths)
