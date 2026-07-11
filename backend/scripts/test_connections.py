"""Teste simples de conexao com PostgreSQL e MinIO."""

import asyncio
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from uuid import uuid4

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import text  # noqa: E402

from app.db.session import engine  # noqa: E402
from app.services.storage import ObjectStorage  # noqa: E402

EXPECTED_TABLES = {
    "arquivos_backup",
    "categorias",
    "desenhos",
    "importacoes",
    "itens_importacao",
    "matrizes",
    "origens_importacao",
}


def test_minio() -> None:
    storage = ObjectStorage()
    storage.ensure_bucket()
    key = f"testes/conexao-{uuid4()}.txt"

    with TemporaryDirectory() as directory:
        file_path = Path(directory) / "conexao.txt"
        file_path.write_text("teste de conexao com MinIO", encoding="utf-8")
        uploaded = False

        try:
            storage.upload_file(file_path, key, "text/plain")
            uploaded = True
            storage.object_exists(key)
        finally:
            if uploaded:
                storage.delete_object(key)


async def main() -> int:
    try:
        async with engine.connect() as connection:
            await connection.execute(text("SELECT 1"))
            result = await connection.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            )
            missing_tables = EXPECTED_TABLES - set(result.scalars())
            if missing_tables:
                tables = ", ".join(sorted(missing_tables))
                raise RuntimeError(f"Migrações pendentes. Tabelas ausentes: {tables}")
        print("[OK] PostgreSQL")

        await asyncio.to_thread(test_minio)
        print("[OK] MinIO (arquivo enviado e removido)")
    except Exception as error:
        print(f"[ERRO] {error}")
        return 1
    finally:
        await engine.dispose()

    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
