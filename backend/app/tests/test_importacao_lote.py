from io import BytesIO

import pytest
from fastapi import UploadFile

from app.services.importacao_lote import ImportacaoArquivoError, ImportacaoLoteService


def test_rejects_mismatched_relative_paths() -> None:
    arquivos = [UploadFile(BytesIO(b"conteudo"), filename="flor.pes")]

    with pytest.raises(ImportacaoArquivoError, match="caminho relativo"):
        ImportacaoLoteService._validate_relative_paths(arquivos, ["pasta/flor.pes", "extra.pes"])


def test_rejects_non_pes_file() -> None:
    with pytest.raises(ImportacaoArquivoError, match=".PES"):
        ImportacaoLoteService._validate_file_name("imagem.png")
