from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.arquivo_backup import ArquivoBackup
    from app.models.desenho import Desenho
    from app.models.item_importacao import ItemImportacao
    from app.models.origem_importacao import OrigemImportacao


class Matriz(Base):
    __tablename__ = "matrizes"

    id: Mapped[int] = mapped_column(primary_key=True)
    desenho_id: Mapped[int] = mapped_column(ForeignKey("desenhos.id", ondelete="CASCADE"), index=True)
    arquivo_backup_id: Mapped[int] = mapped_column(ForeignKey("arquivos_backup.id", ondelete="RESTRICT"), unique=True)
    origem_importacao_id: Mapped[int | None] = mapped_column(
        ForeignKey("origens_importacao.id", ondelete="SET NULL"), index=True
    )
    caminho_relativo_origem: Mapped[str | None] = mapped_column(String(1024))
    formato: Mapped[str] = mapped_column(String(16))
    rotulo_tamanho: Mapped[str | None] = mapped_column(String(120))
    largura_mm: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    altura_mm: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    quantidade_cores: Mapped[int] = mapped_column(Integer)
    quantidade_pontos: Mapped[int] = mapped_column(Integer)
    observacao: Mapped[str | None] = mapped_column(Text)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    desenho: Mapped["Desenho"] = relationship(back_populates="matrizes")
    arquivo_backup: Mapped["ArquivoBackup"] = relationship(back_populates="matriz")
    origem_importacao: Mapped["OrigemImportacao | None"] = relationship(back_populates="matrizes")
    item_importacao: Mapped["ItemImportacao | None"] = relationship(back_populates="matriz", uselist=False)
