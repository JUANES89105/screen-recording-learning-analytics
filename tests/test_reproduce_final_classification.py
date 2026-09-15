from decimal import Decimal
from pathlib import Path

from src.config import load_site_config
from src.reproduce_final_classification import (
    build_candidate_episodes,
    read_csv,
    reproduce_rows,
    summarize,
    verify_rows,
)


ROOT = Path(__file__).resolve().parents[1]


def test_privacy_safe_inputs_reproduce_authoritative_final_dataset():
    config = load_site_config(ROOT / "config" / "sites.yaml")
    reproduced, audit = reproduce_rows(
        read_csv(ROOT / "data" / "processed" / "refinement_input_public.csv"),
        read_csv(
            ROOT
            / "data"
            / "processed"
            / "manual_review_decisions_public.csv"
        ),
        config,
    )
    authoritative = read_csv(
        ROOT
        / "data"
        / "processed"
        / "corpus_100_videos_public_final.csv"
    )
    verification = verify_rows(reproduced, authoritative)
    summary = summarize(reproduced)

    assert audit == {
        "records": 18829,
        "candidate_episodes": 1080,
        "candidate_segments": 4322,
        "temporally_resolved_episodes": 702,
        "temporally_resolved_segments": 1265,
        "manual_episodes": 378,
        "manual_segments": 3057,
    }
    assert verification == {
        "key_matches": 18829,
        "label_matches": 18829,
        "method_matches": 18829,
        "flag_matches": 18829,
        "records": 18829,
    }
    assert summary["counts"] == {
        "Quinan": 13707,
        "YouTube": 1599,
        "Juegos": 971,
        "Wikipedia": 722,
        "Google": 508,
        "Google (Mat)": 427,
        "Screen Recorder": 362,
        "GeoGebra": 272,
        "Otro sitio": 261,
    }
    assert summary["durations"] == {
        "Quinan": Decimal("253043.65"),
        "YouTube": Decimal("2959.37"),
        "Juegos": Decimal("5291.72"),
        "Wikipedia": Decimal("1514.65"),
        "Google": Decimal("4185.48"),
        "Google (Mat)": Decimal("4360.81"),
        "Screen Recorder": Decimal("23488.75"),
        "GeoGebra": Decimal("2541.14"),
        "Otro sitio": Decimal("10590.83"),
    }
    assert summary["total_duration"] == Decimal("307976.40")
    assert summary["transitions"] == 1482


def test_candidate_episode_grouping_uses_historical_three_second_gap():
    rows = [
        {
            "video_id": "V001",
            "start_time_s": "0",
            "end_time_s": "1",
            "requires_review": True,
        },
        {
            "video_id": "V001",
            "start_time_s": "3.5",
            "end_time_s": "4",
            "requires_review": True,
        },
        {
            "video_id": "V001",
            "start_time_s": "7.1",
            "end_time_s": "8",
            "requires_review": True,
        },
    ]

    assert build_candidate_episodes(rows, gap_seconds=3) == [[0, 1], [2]]
