from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import Any, Sequence

import numpy as np
from paddleocr import PaddleOCR

from src.core.schemas import ImageRGB, OCRResult
from src.core.services.ocr_service import OCRService


@dataclass(slots=True)
class OCRProviderSettings:
    """Runtime-tunable OCR provider settings."""

    lang: str = "ru"
    anchor_text: str = "СОБСТВЕННИК"
    anchor_threshold: float = 0.55
    crop_left_ratio: float = 0.05
    crop_right_ratio: float = 0.70
    crop_top_ratio: float = 0.05
    crop_bottom_ratio: float = 0.30


class OCRProvider(OCRService):
    """PaddleOCR-backed implementation with two-stage recognition."""

    def __init__(self, settings: OCRProviderSettings | None = None) -> None:
        self.settings = settings or OCRProviderSettings()
        self.ocr = PaddleOCR(lang=self.settings.lang)

    def extract_text(self, image: ImageRGB) -> OCRResult:
        """
        Run two-stage OCR.

        1) First pass over full image to find anchor and build crop.
        2) Second pass over crop.
        Fallback: if anchor is not found, return first-pass text.
        """
        owner_crop, first_texts, first_scores, anchor_found = self.preprocess(image)
        if not anchor_found:
            return OCRResult(
                text="\n".join(first_texts),
                confidence=self._average_score(first_scores),
            )

        second_pass = self.ocr.predict(np.asarray(owner_crop, dtype=np.uint8))
        payload = self._parse_payload(second_pass)
        texts = [str(t) for t in (payload.get("rec_texts") or [])]
        scores = self._parse_scores(payload.get("rec_scores"))
        return OCRResult(text="\n".join(texts), confidence=self._average_score(scores))

    def preprocess(
        self,
        image: ImageRGB,
    ) -> tuple[ImageRGB, list[str], list[float], bool]:
        """
        First-stage OCR for anchor detection and owner-block crop extraction.

        Returns tuple:
          - crop image (or original image in fallback case)
          - first pass texts
          - first pass scores
          - anchor_found flag
        """
        first_pass = self.ocr.predict(
            np.asarray(image, dtype=np.uint8),
            use_doc_orientation_classify=False,
            use_doc_unwarping=False,
            use_textline_orientation=False,
        )
        payload = self._parse_payload(first_pass)
        texts = [str(t) for t in (payload.get("rec_texts") or [])]
        scores = self._parse_scores(payload.get("rec_scores"))
        boxes = self._parse_boxes(payload)

        anchor_idx, _ = self.extract_anchor(texts)
        if anchor_idx is None or anchor_idx >= len(boxes):
            return image, texts, scores, False

        x1, y1, _, _ = boxes[anchor_idx]
        height, width = image.shape[:2]
        ax1 = max(0, int(x1 - self.settings.crop_left_ratio * width))
        ax2 = min(width, int(x1 + self.settings.crop_right_ratio * width))
        ay1 = max(0, int(y1 - self.settings.crop_top_ratio * height))
        ay2 = min(height, int(y1 + self.settings.crop_bottom_ratio * height))
        if ax2 <= ax1 or ay2 <= ay1:
            return image, texts, scores, False

        owner_crop = image[ay1:ay2, ax1:ax2]
        if owner_crop.size == 0:
            return image, texts, scores, False

        return owner_crop, texts, scores, True

    def extract_anchor(self, texts: Sequence[str]) -> tuple[int | None, float]:
        """Find best fuzzy-matching anchor index in OCR text list."""
        target = self._normalize_token(self.settings.anchor_text)
        best_idx: int | None = None
        best_score = -1.0

        for idx, value in enumerate(texts):
            score = SequenceMatcher(None, self._normalize_token(value), target).ratio()
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is None or best_score < self.settings.anchor_threshold:
            return None, best_score

        return best_idx, best_score

    @staticmethod
    def _normalize_token(value: str) -> str:
        normalized = value.upper().replace("Ё", "Е")
        return "".join(ch for ch in normalized if ch.isalpha())

    @staticmethod
    def _parse_payload(prediction: Any) -> dict[str, Any]:
        if not prediction:
            return {}
        first = prediction[0]
        if isinstance(first, dict):
            payload = first.get("res", first)
            if isinstance(payload, dict):
                return payload
        return {}

    @staticmethod
    def _parse_scores(raw_scores: Any) -> list[float]:
        if raw_scores is None:
            return []
        scores: list[float] = []
        for score in raw_scores:
            try:
                scores.append(float(score))
            except (TypeError, ValueError):
                continue
        return scores

    @staticmethod
    def _parse_boxes(payload: dict[str, Any]) -> list[tuple[int, int, int, int]]:
        raw_boxes = payload.get("rec_boxes")
        if raw_boxes is None:
            boxes_iter = []
        elif isinstance(raw_boxes, np.ndarray):
            boxes_iter = raw_boxes.tolist()
        else:
            boxes_iter = raw_boxes
        boxes: list[tuple[int, int, int, int]] = []
        for box in boxes_iter:
            coords = OCRProvider._box_to_xyxy(box)
            if coords is not None:
                boxes.append(coords)
        if boxes:
            return boxes
        raw_polys = payload.get("rec_polys")
        if raw_polys is None:
            polys_iter = []
        elif isinstance(raw_polys, np.ndarray):
            polys_iter = raw_polys.tolist()
        else:
            polys_iter = raw_polys
        for poly in polys_iter:
            if poly is None or len(poly) == 0:
                continue
            xs = [int(point[0]) for point in poly]
            ys = [int(point[1]) for point in poly]
            boxes.append((min(xs), min(ys), max(xs), max(ys)))
        return boxes

    @staticmethod
    def _box_to_xyxy(box: Any) -> tuple[int, int, int, int] | None:
        if box is None:
            return None
        try:
            if len(box) == 4:
                return (int(box[0]), int(box[1]), int(box[2]), int(box[3]))
        except (TypeError, ValueError):
            return None
        return None

    @staticmethod
    def _average_score(scores: Sequence[float]) -> float | None:
        if not scores:
            return None
        return float(sum(scores) / len(scores))
