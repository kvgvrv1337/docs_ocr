from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(slots=True)
class OCRResult:
    """Text extracted from image by OCR provider."""

    text: str
    confidence: Optional[float] = None


@dataclass(slots=True)
class FIOResult:
    """Extracted person name parts from OCR text."""

    surname: Optional[str] = None
    name: Optional[str] = None
    patronymic: Optional[str] = None


@dataclass(slots=True)
class PipelineResult:
    """Top-level result returned by orchestration layer."""

    fio: FIOResult

    def to_output_dict(self) -> dict[str, Optional[str]]:

        return {
            "фамилия": self.fio.surname,
            "имя": self.fio.name,
            "отчество": self.fio.patronymic,
        }


