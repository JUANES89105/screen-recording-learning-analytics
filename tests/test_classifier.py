from pathlib import Path
import pandas as pd

from src.classifier import RuleBasedClassifier


def test_basic_classification():
    config = Path("config/sites_example.yaml")
    classifier = RuleBasedClassifier(config)
    df = pd.DataFrame({
        "texto_extraido": [
            "Welcome to Moodle - My courses",
            "GeoGebra Classic",
            "OpenAI ChatGPT",
            "unknown application text",
        ]
    })
    out = classifier.classify_dataframe(df)
    assert out["categoria_automatica"].tolist() == [
        "Moodle", "GeoGebra", "ChatGPT", "Otro sitio"
    ]
    assert out["requiere_revision"].tolist() == [False, False, False, True]
