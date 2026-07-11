from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class CategoriaBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    cor: str | None = Field(default=None, max_length=32)
    icone: str | None = Field(default=None, max_length=80)

    @field_validator("nome")
    @classmethod
    def remover_espacos_externos(cls, value: str) -> str:
        nome = value.strip()
        if not nome:
            raise ValueError("O nome da categoria não pode conter apenas espaços.")
        return nome


class CriarCategoriaRequest(CategoriaBase):
    pass


class AtualizarCategoriaRequest(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    cor: str | None = Field(default=None, max_length=32)
    icone: str | None = Field(default=None, max_length=80)

    @field_validator("nome")
    @classmethod
    def remover_espacos_externos(cls, value: str | None) -> str | None:
        if value is None:
            return None

        nome = value.strip()
        if not nome:
            raise ValueError("O nome da categoria não pode conter apenas espaços.")
        return nome


class CategoriaResponse(CategoriaBase):
    id: int
    criado_em: datetime
