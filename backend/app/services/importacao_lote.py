from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import BinaryIO

from fastapi import UploadFile
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.models import ArquivoBackup, Desenho, Importacao, ItemImportacao, Matriz, OrigemImportacao
from app.services.pes_processor import PesMetadata, PesProcessingError, PesProcessor
from app.services.storage import ObjectStorage

logger = logging.getLogger(__name__)


class ImportacaoArquivoError(Exception):
    """Expected error while importing a single file."""


@dataclass(frozen=True)
class ItemImportado:
    id: int
    nome_arquivo: str
    caminho_relativo: str | None
    status: str
    matriz_id: int | None
    motivo_falha: str | None
    desenho_id: int | None = None
    nome: str | None = None
    largura_mm: float | None = None
    altura_mm: float | None = None
    quantidade_pontos: int | None = None
    quantidade_cores: int | None = None


@dataclass(frozen=True)
class ResultadoImportacaoLote:
    id: int
    nome_lote: str
    status: str
    total_arquivos: int
    arquivos_importados: int
    arquivos_com_falha: int
    iniciado_em: datetime
    finalizado_em: datetime | None
    itens: list[ItemImportado]


class ImportacaoLoteService:
    def __init__(
        self,
        settings: Settings | None = None,
        processor: PesProcessor | None = None,
        storage: ObjectStorage | None = None,
    ) -> None:
        self.settings = settings or get_settings()
        self.processor = processor or PesProcessor()
        self.storage = storage or ObjectStorage(self.settings)

    async def importar(
        self,
        session: AsyncSession,
        arquivos: list[UploadFile],
        caminhos_relativos: list[str] | None,
        identificacao_origem: str | None,
        nome_lote: str | None,
    ) -> ResultadoImportacaoLote:
        self._validate_relative_paths(arquivos, caminhos_relativos)
        importacao, origem_id = await self._create_importacao(
            session,
            arquivos,
            identificacao_origem,
            nome_lote,
            caminhos_relativos,
        )
        resultados: list[ItemImportado] = []

        for index, arquivo in enumerate(arquivos):
            caminho_relativo = caminhos_relativos[index] if caminhos_relativos else None
            resultados.append(await self._importar_arquivo(session, importacao, origem_id, arquivo, caminho_relativo))

        importacao.arquivos_importados = sum(item.status == "importado" for item in resultados)
        importacao.arquivos_com_falha = sum(item.status == "falha" for item in resultados)
        importacao.status = "concluida"
        importacao.finalizado_em = datetime.now(timezone.utc)
        await session.commit()

        return ResultadoImportacaoLote(
            id=importacao.id,
            nome_lote=importacao.nome_lote,
            status=importacao.status,
            total_arquivos=importacao.total_arquivos,
            arquivos_importados=importacao.arquivos_importados,
            arquivos_com_falha=importacao.arquivos_com_falha,
            iniciado_em=importacao.iniciado_em,
            finalizado_em=importacao.finalizado_em,
            itens=resultados,
        )

    async def importar_arquivo(
        self,
        session: AsyncSession,
        arquivo: UploadFile,
        caminho_relativo: str | None,
        identificacao_origem: str | None,
    ) -> tuple[ResultadoImportacaoLote, ItemImportado]:
        caminhos = [caminho_relativo] if caminho_relativo else None
        resultado = await self.importar(
            session=session,
            arquivos=[arquivo],
            caminhos_relativos=caminhos,
            identificacao_origem=identificacao_origem,
            nome_lote=Path(arquivo.filename or "arquivo").stem,
        )
        item = resultado.itens[0]
        if item.status == "falha":
            raise ImportacaoArquivoError(item.motivo_falha or "Não foi possível importar o arquivo.")
        return resultado, item

    async def _create_importacao(
        self,
        session: AsyncSession,
        arquivos: list[UploadFile],
        identificacao_origem: str | None,
        nome_lote: str | None,
        caminhos_relativos: list[str] | None,
    ) -> tuple[Importacao, int | None]:
        importacao = Importacao(
            nome_lote=nome_lote or f"Importação de {datetime.now(timezone.utc):%d/%m/%Y %H:%M}",
            status="processando",
            total_arquivos=len(arquivos),
        )
        session.add(importacao)

        origem_id = None
        if identificacao_origem:
            origem = OrigemImportacao(
                identificacao=identificacao_origem,
                tipo="pasta" if caminhos_relativos else "arquivos",
            )
            session.add(origem)
            await session.flush()
            origem_id = origem.id

        await session.commit()
        await session.refresh(importacao)
        return importacao, origem_id

    async def _importar_arquivo(
        self,
        session: AsyncSession,
        importacao: Importacao,
        origem_id: int | None,
        arquivo: UploadFile,
        caminho_relativo: str | None,
    ) -> ItemImportado:
        nome_arquivo = Path(arquivo.filename or "arquivo-sem-nome").name
        uploaded_keys: list[str] = []

        try:
            self._validate_file_name(nome_arquivo)
            with TemporaryDirectory(prefix="importacao-pes-") as directory:
                pes_path = Path(directory) / nome_arquivo
                preview_path = Path(directory) / "preview.png"
                await asyncio.to_thread(self._save_upload, arquivo.file, pes_path)
                metadata = await asyncio.to_thread(self.processor.process, pes_path, preview_path)

                await asyncio.to_thread(self.storage.ensure_bucket)
                design_key = await asyncio.to_thread(self.storage.upload_design, pes_path)
                uploaded_keys.append(design_key)
                preview_key = await asyncio.to_thread(self.storage.upload_preview, preview_path)
                uploaded_keys.append(preview_key)

                return await self._persist_success(
                    session,
                    importacao,
                    origem_id,
                    nome_arquivo,
                    caminho_relativo,
                    metadata,
                    design_key,
                    preview_key,
                    arquivo.content_type,
                )
        except ImportacaoArquivoError as error:
            reason = str(error)
        except PesProcessingError as error:
            reason = str(error)
        except IntegrityError:
            reason = "Esta matriz já foi importada anteriormente."
        except Exception:
            logger.exception("Erro ao importar o arquivo %s", nome_arquivo)
            reason = "Não foi possível processar este arquivo."

        await self._delete_uploaded_files(uploaded_keys)
        return await self._persist_failure(session, importacao, nome_arquivo, caminho_relativo, reason)

    async def _persist_success(
        self,
        session: AsyncSession,
        importacao: Importacao,
        origem_id: int | None,
        nome_arquivo: str,
        caminho_relativo: str | None,
        metadata: PesMetadata,
        design_key: str,
        preview_key: str,
        content_type: str | None,
    ) -> ItemImportado:
        desenho = Desenho(nome=metadata.nome_sugerido, imagem_preview_chave=preview_key)
        backup = ArquivoBackup(
            nome_original=nome_arquivo,
            nome_interno=Path(design_key).name,
            extensao=".pes",
            mime_type=content_type or "application/octet-stream",
            tamanho_bytes=metadata.tamanho_bytes,
            hash_sha256=metadata.hash_sha256,
            chave_storage=design_key,
        )
        matriz = Matriz(
            desenho=desenho,
            arquivo_backup=backup,
            origem_importacao_id=origem_id,
            caminho_relativo_origem=caminho_relativo,
            formato=metadata.formato,
            rotulo_tamanho=f"{metadata.largura_mm:.1f} x {metadata.altura_mm:.1f} mm",
            largura_mm=metadata.largura_mm,
            altura_mm=metadata.altura_mm,
            quantidade_cores=metadata.quantidade_cores,
            quantidade_pontos=metadata.quantidade_pontos,
        )
        item = ItemImportacao(
            importacao_id=importacao.id,
            matriz=matriz,
            nome_arquivo=nome_arquivo,
            caminho_relativo=caminho_relativo,
            status="importado",
            processado_em=datetime.now(timezone.utc),
        )
        session.add(item)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()
            raise

        return ItemImportado(
            id=item.id,
            nome_arquivo=item.nome_arquivo,
            caminho_relativo=item.caminho_relativo,
            status=item.status,
            matriz_id=matriz.id,
            motivo_falha=None,
            desenho_id=desenho.id,
            nome=desenho.nome,
            largura_mm=metadata.largura_mm,
            altura_mm=metadata.altura_mm,
            quantidade_pontos=metadata.quantidade_pontos,
            quantidade_cores=metadata.quantidade_cores,
        )

    async def _persist_failure(
        self,
        session: AsyncSession,
        importacao: Importacao,
        nome_arquivo: str,
        caminho_relativo: str | None,
        reason: str,
    ) -> ItemImportado:
        item = ItemImportacao(
            importacao_id=importacao.id,
            nome_arquivo=nome_arquivo,
            caminho_relativo=caminho_relativo,
            status="falha",
            motivo_falha=reason,
            processado_em=datetime.now(timezone.utc),
        )
        session.add(item)
        await session.commit()
        return ItemImportado(
            id=item.id,
            nome_arquivo=item.nome_arquivo,
            caminho_relativo=item.caminho_relativo,
            status=item.status,
            matriz_id=None,
            motivo_falha=item.motivo_falha,
        )

    async def _delete_uploaded_files(self, keys: list[str]) -> None:
        for key in keys:
            try:
                await asyncio.to_thread(self.storage.delete_object, key)
            except Exception:
                logger.exception("Não foi possível remover o arquivo temporário %s do MinIO", key)

    def _save_upload(self, source: BinaryIO, target_path: Path) -> None:
        source.seek(0)
        size = 0
        with target_path.open("wb") as target:
            while chunk := source.read(1024 * 1024):
                size += len(chunk)
                if size > self.settings.max_upload_size_bytes:
                    raise ImportacaoArquivoError("O arquivo excede o tamanho máximo permitido.")
                target.write(chunk)

    @staticmethod
    def _validate_file_name(name: str) -> None:
        if Path(name).suffix.lower() != ".pes":
            raise ImportacaoArquivoError("Apenas arquivos .PES são aceitos.")

    @staticmethod
    def _validate_relative_paths(arquivos: list[UploadFile], caminhos_relativos: list[str] | None) -> None:
        if not arquivos:
            raise ImportacaoArquivoError("Envie pelo menos um arquivo .PES.")
        if caminhos_relativos is not None and len(caminhos_relativos) != len(arquivos):
            raise ImportacaoArquivoError("Envie um caminho relativo para cada arquivo selecionado.")
