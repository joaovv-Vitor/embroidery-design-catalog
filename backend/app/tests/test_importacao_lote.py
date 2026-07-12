from io import BytesIO

import pytest
from fastapi import UploadFile

from app.services.importacao_lote import ImportacaoArquivoError, ImportacaoLoteService


class _FailureSession:
    def __init__(self) -> None:
        self.added = None
        self.committed = False

    def add(self, item: object) -> None:
        self.added = item

    async def commit(self) -> None:
        self.committed = True


def test_rejects_mismatched_relative_paths() -> None:
    arquivos = [UploadFile(BytesIO(b"conteudo"), filename="flor.pes")]

    with pytest.raises(ImportacaoArquivoError, match="caminho relativo"):
        ImportacaoLoteService._validate_relative_paths(arquivos, ["pasta/flor.pes", "extra.pes"])


def test_rejects_non_pes_file() -> None:
    with pytest.raises(ImportacaoArquivoError, match=".PES"):
        ImportacaoLoteService._validate_file_name("imagem.png")


@pytest.mark.asyncio
async def test_persists_failure_using_import_id_without_orm_reload() -> None:
    session = _FailureSession()

    await ImportacaoLoteService()._persist_failure(
        session,  # type: ignore[arg-type]
        importacao_id=42,
        nome_arquivo="invalido.pes",
        caminho_relativo="pasta/invalido.pes",
        reason="Arquivo inválido.",
    )

    assert session.added.importacao_id == 42  # type: ignore[union-attr]
    assert session.committed is True
