from pathlib import Path

import pytest
from PIL import Image
from pyembroidery import EmbPattern

from app.services.pes_processor import PesProcessingError, PesProcessor


def test_process_generates_preview_and_metadata(tmp_path: Path) -> None:
    pes_path = tmp_path / "flor.pes"
    preview_path = tmp_path / "preview.png"
    pattern = EmbPattern()
    pattern.stitch_abs(0, 0)
    pattern.stitch_abs(100, 200)
    pattern.end()
    pattern.write(str(pes_path))

    metadata = PesProcessor().process(pes_path, preview_path)

    assert metadata.nome_sugerido == "flor"
    assert metadata.formato == "PES"
    assert metadata.largura_mm == 10.0
    assert metadata.altura_mm == 20.0
    assert metadata.quantidade_pontos > 0
    assert metadata.tamanho_bytes == pes_path.stat().st_size
    assert preview_path.exists()


def test_process_rejects_invalid_pes(tmp_path: Path) -> None:
    pes_path = tmp_path / "invalido.pes"
    pes_path.write_text("não é uma matriz PES", encoding="utf-8")

    with pytest.raises(PesProcessingError):
        PesProcessor().process(pes_path, tmp_path / "preview.png")


def test_preview_keeps_pes_vertical_orientation(tmp_path: Path) -> None:
    preview_path = tmp_path / "preview.png"
    pattern = EmbPattern()
    pattern.stitch_abs(0, 0)
    pattern.stitch_abs(100, 200)
    pattern.end()

    PesProcessor._create_preview(pattern, preview_path, 0, 0, 100, 200)

    image = Image.open(preview_path)
    padding = PesProcessor.preview_padding
    assert image.getpixel((padding + 400, padding + 800)) == (31, 41, 55)
    assert image.getpixel((padding + 400, padding)) != (31, 41, 55)


def test_preview_uses_thread_colors(tmp_path: Path) -> None:
    preview_path = tmp_path / "preview.png"
    pattern = EmbPattern()
    pattern.add_thread("#ef4444")
    pattern.stitch_abs(0, 0)
    pattern.stitch_abs(100, 0)
    pattern.color_change()
    pattern.add_thread("#3b82f6")
    pattern.stitch_abs(100, 100)
    pattern.stitch_abs(0, 100)
    pattern.end()

    PesProcessor._create_preview(pattern, preview_path, 0, 0, 100, 100)

    image = Image.open(preview_path)
    padding = PesProcessor.preview_padding
    assert image.getpixel((padding + 400, padding)) == (239, 68, 68)
    assert image.getpixel((padding + 400, padding + 800)) == (59, 130, 246)
