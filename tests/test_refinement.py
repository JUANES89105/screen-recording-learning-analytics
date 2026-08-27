import pandas as pd

from src.refine_classification import refine_row


def test_refinement_is_driven_by_yaml():

    config = {
        "text_column": "ocr",
        "historical_column": "historical",
        "residual_category": "Other",

        "categories": {
            "PlatformA": {
                "historical_labels": ["platforma"],
                "strong_patterns": ["platforma.com"],
            },

            "Search": {
                "historical_labels": ["search"],
                "strong_patterns": ["search.com"],
            },

            "Search (Science)": {
                "derived_from": "Search",
                "derivation": {
                    "type": "term_evidence",
                    "terms": [
                        "physics",
                        "chemistry",
                    ],
                },
            },

            "Reference": {
                "strong_patterns": [
                    "reference.org",
                ],
            },

            "Other": {
                "residual": True,
            },
        },

        "refinement": {
            "preserve_historical": [
                "PlatformA",
            ],

            "historical_derived_rule": {
                "category": "Search",
            },

            "refine_residual_from": [
                "Other",
            ],

            "residual_priority": [
                "Reference",
            ],

            "review_if_detected": [],
        },
    }

    # Historical label preserved
    row = pd.Series({
        "_normalized_text": "anything",
        "historical": "platforma",
    })

    result = refine_row(
        row,
        config,
    )

    assert result[0] == "PlatformA"
    assert result[2] is False

    # Derived category controlled by YAML terms
    row = pd.Series({
        "_normalized_text": (
            "search results about physics"
        ),
        "historical": "search",
    })

    result = refine_row(
        row,
        config,
    )

    assert result[0] == "Search (Science)"
    assert result[2] is False

    # Residual historical case refined by configured strong evidence
    row = pd.Series({
        "_normalized_text": (
            "https://reference.org/article"
        ),
        "historical": "other",
    })

    result = refine_row(
        row,
        config,
    )

    assert result[0] == "Reference"
    assert result[2] is False

    # Unknown residual remains residual and requires review
    row = pd.Series({
        "_normalized_text": (
            "unknown website"
        ),
        "historical": "other",
    })

    result = refine_row(
        row,
        config,
    )

    assert result[0] == "Other"
    assert result[2] is True
