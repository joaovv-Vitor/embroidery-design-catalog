from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.item_importacao import ItemImportacao


class Importacao(Base):
    __tablename__ = "importacoes"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_lote: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(40))
    total_arquivos: Mapped[int] = mapped_column(Integer, server_default="0")
    arquivos_importados: Mapped[int] = mapped_column(Integer, server_default="0")
    arquivos_com_falha: Mapped[int] = mapped_column(Integer, server_default="0")
    iniciado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    finalizado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    itens: Mapped[list["ItemImportacao"]] = relationship(back_populates="importacao", cascade="all, delete-orphan")
