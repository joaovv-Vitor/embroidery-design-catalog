import asyncio
from collections.abc import AsyncIterator
from pathlib import Path
from uuid import uuid4

import boto3
from botocore.client import BaseClient
from botocore.exceptions import ClientError

from app.core.config import Settings, get_settings


class ObjectStorage:
    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.client: BaseClient = boto3.client(
            "s3",
            endpoint_url=self.settings.s3_endpoint_url,
            aws_access_key_id=self.settings.s3_access_key,
            aws_secret_access_key=self.settings.s3_secret_key,
            region_name=self.settings.s3_region,
        )

    def ensure_bucket(self) -> None:
        try:
            self.client.head_bucket(Bucket=self.settings.s3_bucket)
        except ClientError as error:
            error_code = error.response.get("Error", {}).get("Code")
            if error_code not in {"404", "NoSuchBucket", "NotFound"}:
                raise
            self.client.create_bucket(Bucket=self.settings.s3_bucket)

    def upload_file(self, file_path: Path, key: str, content_type: str) -> None:
        self._upload(file_path, key, content_type)

    def object_exists(self, key: str) -> None:
        self.client.head_object(Bucket=self.settings.s3_bucket, Key=key)

    def delete_object(self, key: str) -> None:
        self.client.delete_object(Bucket=self.settings.s3_bucket, Key=key)

    def copy_object(self, source_key: str, destination_key: str) -> None:
        self.client.copy_object(
            Bucket=self.settings.s3_bucket,
            CopySource={"Bucket": self.settings.s3_bucket, "Key": source_key},
            Key=destination_key,
        )

    def upload_design(self, file_path: Path) -> str:
        key = f"matrizes/{uuid4()}.pes"
        self._upload(file_path, key, "application/octet-stream")
        return key

    def upload_preview(self, file_path: Path) -> str:
        key = f"previews/{uuid4()}.png"
        self._upload(file_path, key, "image/png")
        return key

    def get_object(self, key: str):
        return self.client.get_object(Bucket=self.settings.s3_bucket, Key=key)

    async def open_object_stream(self, key: str) -> tuple[str | None, AsyncIterator[bytes]]:
        response = await asyncio.to_thread(self.get_object, key)
        body = response["Body"]

        async def stream() -> AsyncIterator[bytes]:
            try:
                while chunk := await asyncio.to_thread(body.read, 1024 * 1024):
                    yield chunk
            finally:
                await asyncio.to_thread(body.close)

        return response.get("ContentType"), stream()

    async def object_metadata(self, key: str) -> tuple[str | None, int | None]:
        response = await asyncio.to_thread(
            self.client.head_object,
            Bucket=self.settings.s3_bucket,
            Key=key,
        )
        return response.get("ContentType"), response.get("ContentLength")

    def _upload(self, file_path: Path, key: str, content_type: str) -> None:
        self.client.upload_file(
            str(file_path),
            self.settings.s3_bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
