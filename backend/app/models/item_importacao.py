from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.importacao import Importacao
    from app.models.matriz import Matriz


class ItemImportacao(Base):
    __tablename__ = "itens_importacao"

    id: Mapped[int] = mapped_column(primary_key=True)
    importacao_id: Mapped[int] = mapped_column(ForeignKey("importacoes.id", ondelete="CASCADE"), index=True)
    matriz_id: Mapped[int | None] = mapped_column(ForeignKey("matrizes.id", ondelete="SET NULL"), unique=True)
    nome_arquivo: Mapped[str] = mapped_column(String(255))
    caminho_relativo: Mapped[str | None] = mapped_column(String(1024))
    status: Mapped[str] = mapped_column(String(40))
    motivo_falha: Mapped[str | None] = mapped_column(Text)
    processado_em: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    importacao: Mapped["Importacao"] = relationship(back_populates="itens")
    matriz: Mapped["Matriz | None"] = relationship(back_populates="item_importacao")
