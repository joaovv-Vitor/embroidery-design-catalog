from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.item_vitrine import ItemVitrine


class Vitrine(Base):
    __tablename__ = "vitrines"

    id: Mapped[int] = mapped_column(primary_key=True)
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    titulo: Mapped[str] = mapped_column(String(255))
    nome_cliente: Mapped[str | None] = mapped_column(String(255))
    ativa: Mapped[bool] = mapped_column(Boolean, server_default="true")
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expira_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)

    itens: Mapped[list["ItemVitrine"]] = relationship(
        back_populates="vitrine",
        cascade="all, delete-orphan",
        order_by="ItemVitrine.id",
    )
