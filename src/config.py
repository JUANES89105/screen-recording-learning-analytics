from pathlib import Path

import yaml


def load_site_config(path: str | Path) -> dict:
    """
    Load and validate the YAML classification configuration.

    The YAML is the source of truth for:
    - final categories
    - OCR evidence patterns
    - residual category
    - derived categories
    - historical refinement rules
    """

    path = Path(path)

    with path.open(
        "r",
        encoding="utf-8",
    ) as handle:
        config = yaml.safe_load(handle)

    if not isinstance(config, dict):
        raise ValueError(
            "The YAML configuration must contain a mapping."
        )

    required = {
        "text_column",
        "residual_category",
        "categories",
    }

    missing = required.difference(config)

    if missing:
        raise ValueError(
            f"Missing YAML fields: {sorted(missing)}"
        )

    categories = config["categories"]

    if (
        not isinstance(categories, dict)
        or not categories
    ):
        raise ValueError(
            "'categories' must contain at least one category."
        )

    residual = config["residual_category"]

    if residual not in categories:
        raise ValueError(
            "The residual_category must also be declared "
            "inside 'categories'."
        )

    for name, spec in categories.items():

        if spec is None:
            spec = {}

        if not isinstance(spec, dict):
            raise ValueError(
                f"Category '{name}' must contain a mapping."
            )

        is_residual = bool(
            spec.get("residual", False)
        )

        is_derived = (
            "derived_from" in spec
            or "derivation" in spec
        )

        strong_patterns = spec.get(
            "strong_patterns",
            [],
        )

        patterns = spec.get(
            "patterns",
            [],
        )

        historical_labels = spec.get(
            "historical_labels",
            [],
        )

        if not (
            is_residual
            or is_derived
            or strong_patterns
            or patterns
            or historical_labels
        ):
            raise ValueError(
                f"Category '{name}' has no classification rule."
            )

        if is_derived:

            parent = spec.get(
                "derived_from"
            )

            if not parent:
                raise ValueError(
                    f"Derived category '{name}' "
                    "must define 'derived_from'."
                )

            if parent not in categories:
                raise ValueError(
                    f"Derived category '{name}' references "
                    f"unknown parent '{parent}'."
                )

            derivation = spec.get(
                "derivation",
                {},
            )

            if not isinstance(
                derivation,
                dict,
            ):
                raise ValueError(
                    f"'derivation' for '{name}' "
                    "must be a mapping."
                )

    return config
