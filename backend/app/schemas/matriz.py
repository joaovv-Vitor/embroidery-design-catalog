from pydantic import BaseModel, Field, field_validator


class AtualizarMatrizRequest(BaseModel):
    origem_importacao_id: int | None = None
    identificacao_origem: str | None = Field(default=None, max_length=255)
    caminho_relativo_origem: str | None = Field(default=None, max_length=1024)

    @field_validator("identificacao_origem", "caminho_relativo_origem")
    @classmethod
    def normalizar_texto_opcional(cls, value: str | None) -> str | None:
        if value is None:
            return None
        return value.strip() or None


class MatrizAtualizadaResponse(BaseModel):
    id: int
    origem_importacao_id: int | None
    identificacao_origem: str | None
    caminho_relativo_origem: str | None
