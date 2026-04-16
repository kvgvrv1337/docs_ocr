from __future__ import annotations

from typing import Protocol

from src.core.schemas import OCRResult, ImageRGB


class OCRService(Protocol):
    """Contract for OCR providers."""

    def extract_text(self, image: ImageRGB) -> OCRResult:
        """Extract text and optional confidence from image file."""
