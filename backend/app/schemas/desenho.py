from pydantic import BaseModel, Field


class DesenhoResumoResponse(BaseModel):
    id: int
    nome: str
    categoria_id: int | None
    favorito: bool


class AtualizarDesenhoRequest(BaseModel):
    nome: str | None = Field(default=None, max_length=255)
    categoria_id: int | None = Field(default=None, ge=1)


class AtualizarFavoritoRequest(BaseModel):
    favorito: bool
