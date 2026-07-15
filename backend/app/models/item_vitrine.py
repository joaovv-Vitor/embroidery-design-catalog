from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.desenho import Desenho
    from app.models.vitrine import Vitrine


class ItemVitrine(Base):
    __tablename__ = "itens_vitrine"
    __table_args__ = (UniqueConstraint("vitrine_id", "desenho_id", name="uq_itens_vitrine_vitrine_desenho"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    vitrine_id: Mapped[int] = mapped_column(ForeignKey("vitrines.id", ondelete="CASCADE"), index=True)
    desenho_id: Mapped[int | None] = mapped_column(
        ForeignKey("desenhos.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    nome_snapshot: Mapped[str] = mapped_column(String(255))
    preview_chave_snapshot: Mapped[str | None] = mapped_column(String(512))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    vitrine: Mapped["Vitrine"] = relationship(back_populates="itens")
    desenho: Mapped["Desenho | None"] = relationship(back_populates="itens_vitrine")
