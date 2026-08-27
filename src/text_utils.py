import re
import unicodedata


def normalize_text(value) -> str:
    """Normalize OCR text for rule matching."""
    if value is None:
        return ""
    text = str(value).lower().strip()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    text = re.sub(r"\s+", " ", text)
    return text


def contains_pattern(text: str, patterns: list[str]) -> tuple[bool, str | None]:
    normalized = normalize_text(text)
    for pattern in patterns:
        p = normalize_text(pattern)
        if p and p in normalized:
            return True, pattern
    return False, None
