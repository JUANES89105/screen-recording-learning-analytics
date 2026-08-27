from pathlib import Path
import yaml


def load_site_config(path: str | Path) -> dict:
    path = Path(path)
    with path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    if not isinstance(config, dict):
        raise ValueError("The YAML configuration must contain a mapping.")

    required = {"text_column", "residual_category", "categories"}
    missing = required.difference(config)
    if missing:
        raise ValueError(f"Missing YAML fields: {sorted(missing)}")

    if not isinstance(config["categories"], dict) or not config["categories"]:
        raise ValueError("'categories' must contain at least one category.")

    for name, spec in config["categories"].items():
        patterns = (spec or {}).get("patterns", [])
        if not patterns:
            raise ValueError(f"Category '{name}' has no patterns.")

    return config
