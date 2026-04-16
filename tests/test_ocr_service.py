from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image


def test_ocr_provider_extracts_expected_owner_block_from_test3() -> None:
    pytest.importorskip("paddleocr")
    from src.providers.ocr_provider import OCRProvider

    image_path = Path("data/test3.png")
    if not image_path.exists():
        pytest.skip(f"Missing integration test image: {image_path}")

    with Image.open(image_path) as image:
        image_rgb = np.asarray(image.convert("RGB"), dtype=np.uint8)

    provider = OCRProvider()
    result = provider.extract_text(image_rgb)

    expected_lines = [
        "СОБСТВЕННИК",
        "(владелец)",
        "КОБАЛАВА",
        "KOBALAVA",
        "МАКСИМ",
        "MAKSIM",
        "ЮРЬЕВИЧ",
        "СудъектРоссийской Федерации",
        "MockBa",
    ]

    actual_lines = [line.strip() for line in result.text.splitlines() if line.strip()]
    assert actual_lines[: len(expected_lines)] == expected_lines
    assert result.confidence is not None
    assert result.confidence == pytest.approx(0.9, abs=1e-2)
