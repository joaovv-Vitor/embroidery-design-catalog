from pydantic import BaseModel, Field


class DesenhoResumoResponse(BaseModel):
    id: int
    nome: str
    categoria_id: int | None
    favorito: bool


class CategoriaDetalheResponse(BaseModel):
    id: int
    nome: str
    cor: str | None
    icone: str | None


class DesenhoCardResponse(BaseModel):
    id: int
    nome: str
    favorito: bool
    categoria: CategoriaDetalheResponse | None
    preview_url: str | None


class CatalogoDesenhosResponse(BaseModel):
    itens: list[DesenhoCardResponse]
    total: int
    pagina: int
    por_pagina: int


class MatrizVariacaoResponse(BaseModel):
    id: int
    formato: str
    rotulo_tamanho: str | None
    largura_mm: float
    altura_mm: float
    quantidade_cores: int
    quantidade_pontos: int
    origem_identificacao: str | None
    caminho_relativo_origem: str | None
    download_url: str


class DesenhoDetalheResponse(DesenhoResumoResponse):
    descricao: str | None
    categoria: CategoriaDetalheResponse | None
    preview_url: str | None
    matrizes: list[MatrizVariacaoResponse]


class AtualizarDesenhoRequest(BaseModel):
    nome: str | None = Field(default=None, max_length=255)
    categoria_id: int | None = Field(default=None, ge=1)


class AtualizarFavoritoRequest(BaseModel):
    favorito: bool
