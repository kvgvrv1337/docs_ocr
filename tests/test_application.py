from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from src.core.schemas import OCRResult
from src.main import OCRPipelineApp
from src.providers.extraction_provider import ExtractionProvider


class StubOCRService:
    """Deterministic OCR stub for CI-safe pipeline coverage."""

    def __init__(self, text: str, confidence: float = 1.0) -> None:
        self.text = text
        self.confidence = confidence

    def extract_text(self, image: object) -> OCRResult:
        return OCRResult(text=self.text, confidence=self.confidence)


def test_application_run_and_save_with_stubbed_ocr(tmp_path: Path) -> None:
    image_path = tmp_path / "sample.png"
    output_path = tmp_path / "sample.json"
    Image.new("RGB", (64, 32), color="white").save(image_path)

    app = OCRPipelineApp(
        ocr_service=StubOCRService(
            text="\n".join(
                [
                    "СОБСТВЕННИК",
                    "(владелец)",
                    "КОБАЛАВА",
                    "KOBALAVA",
                    "МАКСИМ",
                    "MAKSIM",
                    "ЮРЬЕВИЧ",
                ]
            )
        ),
        extraction_service=ExtractionProvider(),
    )

    saved_path = app.run_and_save(image_path, output_path)

    assert saved_path == output_path
    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload == {
        "фамилия": "Кобалава",
        "имя": "Максим",
        "отчество": "Юрьевич",
    }


@pytest.mark.parametrize(
    ("image_name", "expected"),
    [
        (
            "test3.png",
            {"фамилия": "Кобалава", "имя": "Максим", "отчество": "Юрьевич"},
        ),
        (
            "test4.jpg",
            {"фамилия": "Дауэ", "имя": "Светлана", "отчество": "Александровна"},
        ),
        (
            "test5.jpg",
            {"фамилия": "Солдатова", "имя": "Надежда", "отчество": "Васильевна"},
        ),
    ],
)
def test_application_cli_returns_expected_fio(
    image_name: str,
    expected: dict[str, str],
    tmp_path: Path,
) -> None:
    pytest.importorskip("paddleocr")

    image_path = Path("data") / image_name
    if not image_path.exists():
        pytest.skip(f"Missing integration test image: {image_path}")

    output_path = tmp_path / f"{image_path.stem}.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-m",
            "src.main",
            "--input_path",
            str(image_path),
            "--output_path",
            str(output_path),
            "--max_side",
            "2500",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert completed.returncode == 0, (
        f"CLI failed with code {completed.returncode}\n"
        f"STDOUT:\n{completed.stdout}\n"
        f"STDERR:\n{completed.stderr}"
    )
    assert output_path.exists(), f"CLI did not create output file: {output_path}"

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload == expected
