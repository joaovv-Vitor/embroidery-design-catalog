from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.categoria import Categoria
    from app.models.matriz import Matriz


class Desenho(Base):
    __tablename__ = "desenhos"

    id: Mapped[int] = mapped_column(primary_key=True)
    categoria_id: Mapped[int | None] = mapped_column(ForeignKey("categorias.id", ondelete="SET NULL"), index=True)
    nome: Mapped[str] = mapped_column(String(255))
    descricao: Mapped[str | None] = mapped_column(Text)
    imagem_preview_chave: Mapped[str | None] = mapped_column(String(512))
    favorito: Mapped[bool] = mapped_column(Boolean, server_default="false")
    excluido_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    categoria: Mapped["Categoria | None"] = relationship(back_populates="desenhos")
    matrizes: Mapped[list["Matriz"]] = relationship(back_populates="desenho", cascade="all, delete-orphan")
