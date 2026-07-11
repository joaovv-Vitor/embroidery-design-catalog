from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.matriz import Matriz


class OrigemImportacao(Base):
    __tablename__ = "origens_importacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    identificacao: Mapped[str] = mapped_column(String(255))
    tipo: Mapped[str] = mapped_column(String(80), server_default="manual")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matrizes: Mapped[list["Matriz"]] = relationship(back_populates="origem_importacao")
