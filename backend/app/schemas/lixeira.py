from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class ConfirmarRemocaoRequest(BaseModel):
    confirmar: Literal[True]


class DesenhoLixeiraResponse(BaseModel):
    id: int
    nome: str
    preview_url: str | None
    excluido_em: datetime
    recuperavel_ate: datetime
    aviso: str
