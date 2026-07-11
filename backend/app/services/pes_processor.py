from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw
from pyembroidery import COLOR_CHANGE, END, JUMP, TRIM, EmbPattern


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
    preview_padding = 40
    preview_largest_side = 800
    preview_background = "#f8fafc"
    preview_canvas = "#ffffff"
    preview_grid = "#e2e8f0"
    preview_stitch_fallback = "#1f2937"

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
        padding = PesProcessor.preview_padding
        largest_side = PesProcessor.preview_largest_side
        width = max(max_x - min_x, 1)
        height = max(max_y - min_y, 1)
        scale = min(largest_side / width, largest_side / height)
        image_size = (int(width * scale) + 2 * padding, int(height * scale) + 2 * padding)
        image = Image.new("RGB", image_size, PesProcessor.preview_background)
        draw = ImageDraw.Draw(image)
        canvas_box = (padding, padding, image_size[0] - padding, image_size[1] - padding)
        draw.rounded_rectangle(canvas_box, radius=18, fill=PesProcessor.preview_canvas, outline="#cbd5e1", width=2)

        grid_step = max(40, int(scale * 10))
        for x in range(padding + grid_step, image_size[0] - padding, grid_step):
            draw.line((x, padding, x, image_size[1] - padding), fill=PesProcessor.preview_grid, width=1)
        for y in range(padding + grid_step, image_size[1] - padding, grid_step):
            draw.line((padding, y, image_size[0] - padding, y), fill=PesProcessor.preview_grid, width=1)

        line_width = max(2, int(scale / 10))
        thread_index = 0
        points: list[tuple[float, float]] = []
        for x, y, command in pattern.stitches:
            point = ((x - min_x) * scale + padding, (y - min_y) * scale + padding)
            command &= 0xFF
            if command in {COLOR_CHANGE, END, JUMP, TRIM}:
                PesProcessor._draw_stitches(draw, points, PesProcessor._thread_color(pattern, thread_index), line_width)
                points = []
                if command == COLOR_CHANGE:
                    thread_index += 1
                continue
            points.append(point)

        PesProcessor._draw_stitches(draw, points, PesProcessor._thread_color(pattern, thread_index), line_width)

        preview_path.parent.mkdir(parents=True, exist_ok=True)
        image.save(preview_path, format="PNG")

    @staticmethod
    def _thread_color(pattern: EmbPattern, thread_index: int) -> str:
        if thread_index < len(pattern.threadlist):
            return pattern.threadlist[thread_index].hex_color()
        return PesProcessor.preview_stitch_fallback

    @staticmethod
    def _draw_stitches(
        draw: ImageDraw.ImageDraw,
        points: list[tuple[float, float]],
        color: str,
        line_width: int,
    ) -> None:
        if len(points) > 1:
            draw.line(points, fill=color, width=line_width, joint="curve")
        elif points:
            x, y = points[0]
            radius = max(2, line_width)
            draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)
