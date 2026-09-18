from pathlib import Path
from unittest.mock import patch

from PIL import Image

from src.extraction import run_ocr


def create_test_image(tmp_path):
    image_path = tmp_path / "test.png"
    Image.new("RGB", (100, 100), "white").save(image_path)
    return image_path


def test_psm11_replaces_short_psm6_when_longer(tmp_path):
    create_test_image(tmp_path)

    with patch(
        "src.extraction.pytesseract.image_to_string",
        side_effect=[
            "short text",
            "this is a substantially longer OCR result recovered with PSM 11",
        ],
    ) as mock_ocr:
        df = run_ocr(tmp_path)

    assert mock_ocr.call_count == 2
    assert df.loc[0, "ocr_mode"] == "psm11_fallback"
    assert "substantially longer" in df.loc[0, "texto"]


def test_psm6_is_retained_when_fallback_is_not_better(tmp_path):
    create_test_image(tmp_path)

    with patch(
        "src.extraction.pytesseract.image_to_string",
        side_effect=[
            "short OCR text",
            "less",
        ],
    ) as mock_ocr:
        df = run_ocr(tmp_path)

    assert mock_ocr.call_count == 2
    assert df.loc[0, "ocr_mode"] == "psm6"
    assert df.loc[0, "texto"] == "short OCR text"


def test_psm11_is_not_called_when_psm6_has_sufficient_text(tmp_path):
    create_test_image(tmp_path)

    long_text = (
        "This OCR result contains more than forty characters "
        "and therefore does not require fallback."
    )

    with patch(
        "src.extraction.pytesseract.image_to_string",
        return_value=long_text,
    ) as mock_ocr:
        df = run_ocr(tmp_path)

    assert mock_ocr.call_count == 1
    assert df.loc[0, "ocr_mode"] == "psm6"
    assert df.loc[0, "texto"] == long_text
