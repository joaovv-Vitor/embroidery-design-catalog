from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class CriarVitrineRequest(BaseModel):
    desenho_ids: list[int] = Field(min_length=1)
    titulo: str = Field(default="Opções de bordado", max_length=255)
    nome_cliente: str | None = Field(default=None, max_length=255)

    @field_validator("desenho_ids")
    @classmethod
    def validar_desenhos(cls, desenho_ids: list[int]) -> list[int]:
        if any(desenho_id < 1 for desenho_id in desenho_ids):
            raise ValueError("Os IDs dos desenhos devem ser maiores que zero.")
        if len(desenho_ids) != len(set(desenho_ids)):
            raise ValueError("Um desenho não pode ser selecionado mais de uma vez.")
        return desenho_ids

    @field_validator("titulo", mode="before")
    @classmethod
    def normalizar_titulo(cls, titulo: object) -> str:
        if titulo is None:
            return "Opções de bordado"
        if not isinstance(titulo, str):
            return titulo  # type: ignore[return-value]
        return titulo.strip() or "Opções de bordado"

    @field_validator("nome_cliente", mode="before")
    @classmethod
    def normalizar_nome_cliente(cls, nome_cliente: object) -> object:
        if isinstance(nome_cliente, str):
            return nome_cliente.strip() or None
        return nome_cliente


class ItemVitrineResponse(BaseModel):
    id: int
    desenho_id: int | None
    nome: str
    preview_url: str | None


class VitrineResponse(BaseModel):
    titulo: str
    nome_cliente: str | None
    criado_em: datetime
    expira_em: datetime
    quantidade_desenhos: int
    itens: list[ItemVitrineResponse]


class CriarVitrineResponse(VitrineResponse):
    token: str
    link_publico: str


class ItemVitrinePublicaResponse(BaseModel):
    numero: int
    nome: str
    preview_url: str | None


class VitrinePublicaResponse(BaseModel):
    titulo: str
    nome_cliente: str | None
    expira_em: datetime
    quantidade_desenhos: int
    itens: list[ItemVitrinePublicaResponse]


class AtualizarStatusVitrineRequest(BaseModel):
    ativa: bool
    confirmar: Literal[True]


class StatusVitrineResponse(BaseModel):
    id: int
    ativa: bool


class ConfirmarExclusaoVitrineRequest(BaseModel):
    confirmar: Literal[True]


class VitrineGerencialResponse(BaseModel):
    id: int
    titulo: str
    quantidade_desenhos: int
    criado_em: datetime
    expira_em: datetime
    status: Literal["ativa", "expirada", "desativada"]
    link_publico: str | None
