from __future__ import annotations

from typing import Protocol

from src.core.schemas import FIOResult


class ExtractionService(Protocol):
    """Contract for FIO extraction providers."""

    def extract_fio(self, text: str) -> FIOResult:
        """Extract surname, name and patronymic from OCR text."""
