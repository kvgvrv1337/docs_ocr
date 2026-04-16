from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from src.core.schemas import ImageRGB, PipelineResult
from src.core.services.extraction_service import ExtractionService
from src.core.services.ocr_service import OCRService


class OCRPipelineApp:
    """Application orchestration: image -> OCR -> FIO extraction -> JSON."""

    def __init__(
        self,
        ocr_service: OCRService,
        extraction_service: ExtractionService,
        *,
        max_side: int | None = 2500,
    ) -> None:
        self.ocr_service = ocr_service
        self.extraction_service = extraction_service
        self.max_side = max_side

    def load_image(self, image_path: str | Path) -> Image.Image:
        """Load an image from disk and normalize to RGB."""
        path = Path(image_path)
        with Image.open(path) as img:
            return img.convert("RGB")

    def preprocess_image(self, image: Image.Image) -> ImageRGB:
        """Downscale image if needed and convert to numpy RGB uint8."""
        resized = self.downscale_max_side(image, max_side=self.max_side)
        return np.asarray(resized, dtype=np.uint8)

    def downscale_max_side(
        self,
        image: Image.Image,
        max_side: int | None = 2500,
    ) -> Image.Image:
        """Resize so max(width, height) <= max_side, preserving aspect ratio."""
        if max_side is None:
            return image

        width, height = image.size
        long_side = max(width, height)
        if long_side <= max_side:
            return image

        scale = max_side / long_side
        new_size = (int(round(width * scale)), int(round(height * scale)))
        return image.resize(new_size, Image.Resampling.LANCZOS)

    def run(self, image_path: str | Path) -> PipelineResult:
        """Run full pipeline and return structured FIO result."""
        image = self.load_image(image_path)
        image_rgb = self.preprocess_image(image)

        ocr_result = self.ocr_service.extract_text(image_rgb)
        fio_result = self.extraction_service.extract_fio(ocr_result.text)

        return PipelineResult(fio=fio_result)

    def save_output(
        self,
        result: PipelineResult,
        output_path: str | Path,
    ) -> Path:
        """Persist result JSON to output path."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload: dict[str, Any] = result.to_output_dict()
        path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    def run_and_save(
        self,
        image_path: str | Path,
        output_path: str | Path | None = None,
    ) -> Path:
        """Run pipeline and save output JSON."""
        result = self.run(image_path)
        target = Path(output_path) if output_path else self.default_output_path(image_path)
        return self.save_output(result, target)

    @staticmethod
    def default_output_path(image_path: str | Path) -> Path:
        """Build default JSON path next to input image."""
        source = Path(image_path)
        return source.with_suffix(".json")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OCR pipeline skeleton")
    parser.add_argument("image_path", help="Input image path")
    parser.add_argument("--output", help="Output JSON path")
    parser.add_argument(
        "--max-side",
        type=int,
        default=2500,
        help="Max image side for downsampling (set <=0 to disable)",
    )
    return parser.parse_args()


def run_cli(
    ocr_service: OCRService,
    extraction_service: ExtractionService,
) -> Path:
    """
    CLI facade that still uses dependency injection.

    Providers should be created by composition root and passed in.
    """
    args = parse_args()
    max_side = args.max_side if args.max_side > 0 else None

    app = OCRPipelineApp(
        ocr_service=ocr_service,
        extraction_service=extraction_service,
        max_side=max_side,
    )
    return app.run_and_save(args.image_path, args.output)


if __name__ == "__main__":
    raise SystemExit(
        "Wire concrete providers and call run_cli(ocr_service, extraction_service)."
    )
