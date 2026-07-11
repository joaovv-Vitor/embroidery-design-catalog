from datetime import datetime

from pydantic import BaseModel, Field


class ItemImportacaoLoteResponse(BaseModel):
    id: int
    nome_arquivo: str
    caminho_relativo: str | None
    status: str
    matriz_id: int | None
    motivo_falha: str | None


class ImportacaoLoteResponse(BaseModel):
    id: int
    nome_lote: str
    status: str
    total_arquivos: int
    arquivos_importados: int
    arquivos_com_falha: int
    iniciado_em: datetime
    finalizado_em: datetime | None
    itens: list[ItemImportacaoLoteResponse]


class ImportacaoArquivoResponse(BaseModel):
    importacao_id: int
    item_importacao_id: int
    desenho_id: int
    matriz_id: int
    nome: str
    largura_mm: float
    altura_mm: float
    quantidade_pontos: int
    quantidade_cores: int


class AtualizarItemImportacaoRequest(BaseModel):
    nome: str | None = Field(default=None, max_length=255)
    descricao: str | None = None
    rotulo_tamanho: str | None = Field(default=None, max_length=120)
    largura_mm: float | None = Field(default=None, ge=0)
    altura_mm: float | None = Field(default=None, ge=0)
    quantidade_cores: int | None = Field(default=None, ge=0)
    quantidade_pontos: int | None = Field(default=None, ge=0)
    observacao: str | None = None
