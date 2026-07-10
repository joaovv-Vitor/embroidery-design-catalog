"""Teste simples de conexao com PostgreSQL e MinIO."""

import asyncio
import sys
from tempfile import TemporaryDirectory
from pathlib import Path
from uuid import uuid4

BACKEND_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_ROOT))

from sqlalchemy import text

from app.db.session import engine
from app.services.storage import ObjectStorage


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
