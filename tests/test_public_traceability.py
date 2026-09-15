import csv
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"


def read_csv(name):
    with (PROCESSED / name).open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def temporal_key(row):
    return (
        row["video_id"],
        row["start_time_s"],
        row["end_time_s"],
        row["duration_s"],
    )


def test_public_validation_manifest_links_to_authoritative_segments():
    final_rows = read_csv("corpus_100_videos_public_final.csv")
    refinement_rows = read_csv("refinement_input_public.csv")
    manifest = read_csv("human_validation_sample_manifest.csv")
    annotations = read_csv("human_validation_annotations.csv")

    final_by_key = {temporal_key(row): row for row in final_rows}
    refinement_by_key = {temporal_key(row): row for row in refinement_rows}
    annotations_by_image = {row["image_id"]: row for row in annotations}

    assert len(final_by_key) == 18829
    assert len(refinement_by_key) == 18829
    assert len(manifest) == 450
    assert len({row["image_id"] for row in manifest}) == 450
    assert len({row["segment_id"] for row in manifest}) == 450
    assert len({row["video_id"] for row in manifest}) == 85
    assert Counter(row["pipeline_category"] for row in manifest) == {
        "Quinan": 50,
        "Google": 50,
        "Google (Mat)": 50,
        "GeoGebra": 50,
        "Wikipedia": 50,
        "YouTube": 50,
        "Juegos": 50,
        "Screen Recorder": 50,
        "Otro sitio": 50,
    }

    for row in manifest:
        key = temporal_key(row)
        final = final_by_key[key]
        refinement = refinement_by_key[key]
        annotation = annotations_by_image[row["image_id"]]
        assert row["segment_id"] == refinement["segment_id"]
        assert row["pipeline_category"] == final["category"]
        assert row["classification_method"] == final["classification_method"]
        assert row["temporal_interpolation"] == final["temporal_interpolation"]
        assert row["manual_review"] == final["manual_review"]
        assert annotation["pipeline_category"] == final["category"]
