from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


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
    assert image_path.exists(), f"Missing test image: {image_path}"

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
