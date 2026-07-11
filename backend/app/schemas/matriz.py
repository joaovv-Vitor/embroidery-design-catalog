from pydantic import BaseModel, Field


class AtualizarMatrizRequest(BaseModel):
    origem_importacao_id: int | None = None
    caminho_relativo_origem: str | None = Field(default=None, max_length=1024)
