from pathlib import Path

import pandas as pd
import pytest
from sklearn.metrics import accuracy_score, cohen_kappa_score


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "human_validation_annotations.csv"


def test_human_validation_metrics():
    df = pd.read_csv(DATA)

    assert len(df) == 450

    agreement = df["EV01"] == df["EV02"]

    assert int(agreement.sum()) == 424
    assert agreement.mean() == pytest.approx(424 / 450)
    assert agreement.mean() == pytest.approx(0.9422222222)

    kappa = cohen_kappa_score(df["EV01"], df["EV02"])
    assert kappa == pytest.approx(0.933789, abs=1e-6)

    ev01_accuracy = accuracy_score(
        df["EV01"],
        df["pipeline_category"],
    )
    ev02_accuracy = accuracy_score(
        df["EV02"],
        df["pipeline_category"],
    )

    consensus = df.loc[agreement]

    consensus_accuracy = accuracy_score(
        consensus["EV01"],
        consensus["pipeline_category"],
    )

    assert ev01_accuracy == pytest.approx(0.7266666667)
    assert ev02_accuracy == pytest.approx(0.7155555556)
    assert consensus_accuracy == pytest.approx(0.7405660377)
