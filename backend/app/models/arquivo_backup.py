from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.matriz import Matriz


class ArquivoBackup(Base):
    __tablename__ = "arquivos_backup"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome_original: Mapped[str] = mapped_column(String(255))
    nome_interno: Mapped[str] = mapped_column(String(255))
    extensao: Mapped[str] = mapped_column(String(16))
    mime_type: Mapped[str] = mapped_column(String(120))
    tamanho_bytes: Mapped[int] = mapped_column(BigInteger)
    hash_sha256: Mapped[str] = mapped_column(String(64), unique=True)
    chave_storage: Mapped[str] = mapped_column(String(512))
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    matriz: Mapped["Matriz | None"] = relationship(back_populates="arquivo_backup", uselist=False)
