from typing import Annotated

from fastapi import APIRouter, File, Form, HTTPException, Path, UploadFile, status
from pydantic import TypeAdapter, ValidationError
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.db.session import DbSession
from app.models import Importacao, ItemImportacao, Matriz
from app.schemas.importacao import (
    AtualizarItemImportacaoRequest,
    ImportacaoArquivoResponse,
    ImportacaoLoteResponse,
    ItemImportacaoLoteResponse,
)
from app.services.importacao_lote import ImportacaoArquivoError, ImportacaoLoteService, ResultadoImportacaoLote

router = APIRouter(prefix="/api/v1/importacoes", tags=["importações"])
relative_paths_adapter = TypeAdapter(list[str])


def _parse_caminhos_relativos(value: str) -> list[str] | None:
    try:
        paths = relative_paths_adapter.validate_json(value)
    except ValidationError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail='caminhos_relativos deve ser um JSON como ["pasta/flor.pes"].',
        ) from error
    return paths or None


def _to_lote_response(result: ResultadoImportacaoLote) -> ImportacaoLoteResponse:
    return ImportacaoLoteResponse(
        id=result.id,
        nome_lote=result.nome_lote,
        status=result.status,
        total_arquivos=result.total_arquivos,
        arquivos_importados=result.arquivos_importados,
        arquivos_com_falha=result.arquivos_com_falha,
        iniciado_em=result.iniciado_em,
        finalizado_em=result.finalizado_em,
        itens=[
            ItemImportacaoLoteResponse(
                id=item.id,
                nome_arquivo=item.nome_arquivo,
                caminho_relativo=item.caminho_relativo,
                status=item.status,
                matriz_id=item.matriz_id,
                motivo_falha=item.motivo_falha,
            )
            for item in result.itens
        ],
    )


@router.post("/lote", status_code=status.HTTP_201_CREATED)
async def importar_lote(
    arquivos: Annotated[list[UploadFile], File(description="Arquivos .PES a serem importados")],
    session: DbSession,
    caminhos_relativos: Annotated[
        str,
        Form(description='JSON na mesma ordem dos arquivos. Exemplo: ["pasta/flor.pes"]'),
    ] = "[]",
    identificacao_origem: Annotated[str, Form(max_length=255)] = "",
    nome_lote: Annotated[str, Form(max_length=255)] = "",
) -> ImportacaoLoteResponse:
    paths = _parse_caminhos_relativos(caminhos_relativos)
    try:
        result = await ImportacaoLoteService().importar(
            session,
            arquivos,
            paths,
            identificacao_origem.strip() or None,
            nome_lote.strip() or None,
        )
    except ImportacaoArquivoError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error

    return _to_lote_response(result)


@router.post("/arquivo", status_code=status.HTTP_201_CREATED)
async def importar_arquivo(
    arquivo: Annotated[UploadFile, File(description="Arquivo .PES a ser importado")],
    session: DbSession,
    caminho_relativo: Annotated[str | None, Form(max_length=1024)] = None,
    identificacao_origem: Annotated[str | None, Form(max_length=255)] = None,
) -> ImportacaoArquivoResponse:
    try:
        resultado, item = await ImportacaoLoteService().importar_arquivo(
            session,
            arquivo,
            caminho_relativo,
            identificacao_origem,
        )
    except ImportacaoArquivoError as error:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=str(error)) from error

    if None in {
        item.desenho_id,
        item.matriz_id,
        item.nome,
        item.largura_mm,
        item.altura_mm,
        item.quantidade_pontos,
        item.quantidade_cores,
    }:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Resultado da importação incompleto.",
        )

    return ImportacaoArquivoResponse(
        importacao_id=resultado.id,
        item_importacao_id=item.id,
        desenho_id=item.desenho_id,
        matriz_id=item.matriz_id,
        nome=item.nome,
        largura_mm=item.largura_mm,
        altura_mm=item.altura_mm,
        quantidade_pontos=item.quantidade_pontos,
        quantidade_cores=item.quantidade_cores,
    )


@router.get("/{importacao_id}")
async def obter_importacao(
    importacao_id: Annotated[int, Path(ge=1)],
    session: DbSession,
) -> ImportacaoLoteResponse:
    query = (
        select(Importacao)
        .where(Importacao.id == importacao_id)
        .options(selectinload(Importacao.itens))
    )
    importacao = (await session.execute(query)).scalar_one_or_none()
    if importacao is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Importação não encontrada.")

    return ImportacaoLoteResponse(
        id=importacao.id,
        nome_lote=importacao.nome_lote,
        status=importacao.status,
        total_arquivos=importacao.total_arquivos,
        arquivos_importados=importacao.arquivos_importados,
        arquivos_com_falha=importacao.arquivos_com_falha,
        iniciado_em=importacao.iniciado_em,
        finalizado_em=importacao.finalizado_em,
        itens=[
            ItemImportacaoLoteResponse(
                id=item.id,
                nome_arquivo=item.nome_arquivo,
                caminho_relativo=item.caminho_relativo,
                status=item.status,
                matriz_id=item.matriz_id,
                motivo_falha=item.motivo_falha,
            )
            for item in importacao.itens
        ],
    )


@router.patch("/itens/{item_id}")
async def atualizar_item_importacao(
    item_id: Annotated[int, Path(ge=1)],
    dados: AtualizarItemImportacaoRequest,
    session: DbSession,
) -> ItemImportacaoLoteResponse:
    query = (
        select(ItemImportacao)
        .where(ItemImportacao.id == item_id)
        .options(selectinload(ItemImportacao.matriz).selectinload(Matriz.desenho))
    )
    item = (await session.execute(query)).scalar_one_or_none()
    if item is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item de importação não encontrado.")
    if item.matriz is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Não é possível editar um item com falha.")

    values = dados.model_dump(exclude_unset=True)
    desenho = item.matriz.desenho
    if "nome" in values:
        desenho.nome = values["nome"]
    if "descricao" in values:
        desenho.descricao = values["descricao"]
    for field in ("rotulo_tamanho", "largura_mm", "altura_mm", "quantidade_cores", "quantidade_pontos", "observacao"):
        if field in values:
            setattr(item.matriz, field, values[field])

    await session.commit()
    return ItemImportacaoLoteResponse(
        id=item.id,
        nome_arquivo=item.nome_arquivo,
        caminho_relativo=item.caminho_relativo,
        status=item.status,
        matriz_id=item.matriz_id,
        motivo_falha=item.motivo_falha,
    )
