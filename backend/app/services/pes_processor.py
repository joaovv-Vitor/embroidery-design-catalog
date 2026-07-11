from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw
from pyembroidery import EmbPattern


class PesProcessingError(Exception):
    """Raised when a PES file cannot be processed."""


@dataclass(frozen=True)
class PesMetadata:
    nome_sugerido: str
    formato: str
    largura_mm: float
    altura_mm: float
    quantidade_pontos: int
    quantidade_cores: int
    hash_sha256: str
    tamanho_bytes: int
    preview_path: Path


class PesProcessor:
    units_per_millimeter = 10

    def process(self, pes_path: Path, preview_path: Path) -> PesMetadata:
        try:
            pattern = EmbPattern()
            pattern.read(str(pes_path))
            min_x, min_y, max_x, max_y = pattern.bounds()
        except Exception as error:
            raise PesProcessingError("Arquivo PES inválido ou corrompido.") from error

        if not all(math.isfinite(value) for value in (min_x, min_y, max_x, max_y)):
            raise PesProcessingError("A matriz PES não contém pontos válidos.")

        self._create_preview(pattern, preview_path, min_x, min_y, max_x, max_y)

        return PesMetadata(
            nome_sugerido=pes_path.stem,
            formato="PES",
            largura_mm=round((max_x - min_x) / self.units_per_millimeter, 2),
            altura_mm=round((max_y - min_y) / self.units_per_millimeter, 2),
            quantidade_pontos=pattern.count_stitches(),
            quantidade_cores=pattern.count_threads(),
            hash_sha256=self._calculate_hash(pes_path),
            tamanho_bytes=pes_path.stat().st_size,
            preview_path=preview_path,
        )

    @staticmethod
    def _calculate_hash(file_path: Path) -> str:
        digest = hashlib.sha256()
        with file_path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    @staticmethod
    def _create_preview(
        pattern: EmbPattern,
        preview_path: Path,
        min_x: float,
        min_y: float,
        max_x: float,
        max_y: float,
    ) -> None:
        padding = 24
        largest_side = 800
        width = max(max_x - min_x, 1)
        height = max(max_y - min_y, 1)
        scale = min(largest_side / width, largest_side / height)
        image_size = (int(width * scale) + 2 * padding, int(height * scale) + 2 * padding)
        image = Image.new("RGB", image_size, "white")
        draw = ImageDraw.Draw(image)

        points = [
            ((x - min_x) * scale + padding, (max_y - y) * scale + padding)
            for x, y, _ in pattern.stitches
        ]
        if len(points) > 1:
            draw.line(points, fill="#202020", width=max(1, int(scale / 12)), joint="curve")
        elif points:
            x, y = points[0]
            draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill="#202020")

        preview_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(preview_path, format="PNG")
