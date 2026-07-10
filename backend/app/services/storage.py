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
        except ClientError:
            self.client.create_bucket(Bucket=self.settings.s3_bucket)

    def upload_file(self, file_path: Path, key: str, content_type: str) -> None:
        self._upload(file_path, key, content_type)

    def object_exists(self, key: str) -> None:
        self.client.head_object(Bucket=self.settings.s3_bucket, Key=key)

    def delete_object(self, key: str) -> None:
        self.client.delete_object(Bucket=self.settings.s3_bucket, Key=key)

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

    def _upload(self, file_path: Path, key: str, content_type: str) -> None:
        self.client.upload_file(
            str(file_path),
            self.settings.s3_bucket,
            key,
            ExtraArgs={"ContentType": content_type},
        )
