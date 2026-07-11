from pathlib import Path

import pytest
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
