from __future__ import annotations

import hashlib
import json
import urllib.request
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class ModelDescriptor:
    """Manifest entry for a single model artifact."""

    file_name: str
    url: str
    sha256: str


class ModelStore:
    """Minimal model downloader + verifier + local cache manager."""

    def __init__(self, manifest_path: Path, models_dir: Path) -> None:
        self.manifest_path = manifest_path
        self.models_dir = models_dir

    def ensure_model(self, model_name: str) -> Path:
        """
        Ensure model exists locally and matches checksum.

        Expected manifest shape:
        {
          "models": {
            "ocr": {
              "file_name": "ocr.onnx",
              "url": "https://...",
              "sha256": "..."
            }
          }
        }
        """
        descriptor = self._get_descriptor(model_name)
        self.models_dir.mkdir(parents=True, exist_ok=True)

        target = self.models_dir / descriptor.file_name
        if target.exists() and self._verify_sha256(target, descriptor.sha256):
            return target

        self._download(descriptor.url, target)
        if not self._verify_sha256(target, descriptor.sha256):
            target.unlink(missing_ok=True)
            raise ValueError(f"Checksum mismatch for model '{model_name}'")

        return target

    def _get_descriptor(self, model_name: str) -> ModelDescriptor:
        raw = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        try:
            data = raw["models"][model_name]
            return ModelDescriptor(
                file_name=data["file_name"],
                url=data["url"],
                sha256=data["sha256"],
            )
        except KeyError as exc:
            raise KeyError(f"Model '{model_name}' not found in manifest") from exc

    @staticmethod
    def _download(url: str, target_path: Path) -> None:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        with urllib.request.urlopen(url) as response:
            target_path.write_bytes(response.read())

    @staticmethod
    def _verify_sha256(path: Path, expected_sha256: str) -> bool:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        return digest.lower() == expected_sha256.lower()
