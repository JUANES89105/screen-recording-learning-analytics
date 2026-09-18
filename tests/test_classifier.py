from pathlib import Path
import pandas as pd

from src.classifier import RuleBasedClassifier


def test_basic_classification():
    config = Path("config/sites_example.yaml")
    classifier = RuleBasedClassifier(config)
    df = pd.DataFrame({
        "texto": [
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


def test_classifier_is_driven_by_yaml(tmp_path):

    config = tmp_path / "custom_sites.yaml"

    config.write_text(
        """
text_column: ocr

residual_category: Other

categories:

  Desmos:
    patterns:
      - desmos

  WolframAlpha:
    patterns:
      - wolframalpha

  Other:
    residual: true
""",
        encoding="utf-8",
    )

    classifier = RuleBasedClassifier(config)

    assert (
        classifier.classify_text(
            "Working in the Desmos calculator"
        ).category
        == "Desmos"
    )

    assert (
        classifier.classify_text(
            "Searching with WolframAlpha"
        ).category
        == "WolframAlpha"
    )

    assert (
        classifier.classify_text(
            "Completely unknown website"
        ).category
        == "Other"
    )
