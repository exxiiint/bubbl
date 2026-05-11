from __future__ import annotations

import json
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from uuid import UUID, uuid4

from fastapi import UploadFile
from minio import Minio
from minio.error import S3Error
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.media import MediaObject


@dataclass(frozen=True)
class StoredObject:
    bucket: str
    object_key: str
    public_url: str
    content_type: str
    size_bytes: int


class ObjectStorage:
    def __init__(self) -> None:
        self.client = Minio(
            endpoint=settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        self.bucket = settings.minio_bucket

    def ensure_bucket(self) -> None:
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

        policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Action": ["s3:GetObject"],
                    "Resource": [f"arn:aws:s3:::{self.bucket}/*"],
                }
            ],
        }
        self.client.set_bucket_policy(self.bucket, json.dumps(policy))

    def upload_bytes(self, data: bytes, owner_id: UUID, content_type: str, prefix: str, suffix: str) -> StoredObject:
        safe_suffix = suffix if suffix.startswith(".") else f".{suffix}"
        object_key = f"{prefix}/{owner_id}/{uuid4()}{safe_suffix}"
        self.client.put_object(
            bucket_name=self.bucket,
            object_name=object_key,
            data=BytesIO(data),
            length=len(data),
            content_type=content_type,
        )
        return StoredObject(
            bucket=self.bucket,
            object_key=object_key,
            public_url=f"{settings.public_media_base_url}/{object_key}",
            content_type=content_type,
            size_bytes=len(data),
        )

    def upload_file(self, file: UploadFile, owner_id: UUID, prefix: str) -> StoredObject:
        content = file.file.read()
        if not content:
            raise ValueError("Файл пустой")
        content_type = file.content_type or "application/octet-stream"
        extension = Path(file.filename or "upload.bin").suffix or ".bin"
        return self.upload_bytes(content, owner_id, content_type, prefix, extension)


storage = ObjectStorage()


def save_media_record(db: Session, owner_id: UUID, stored: StoredObject) -> MediaObject:
    media = MediaObject(
        owner_id=owner_id,
        bucket=stored.bucket,
        object_key=stored.object_key,
        content_type=stored.content_type,
        size_bytes=stored.size_bytes,
    )
    db.add(media)
    db.flush()
    return media


def safe_ensure_bucket() -> None:
    try:
        storage.ensure_bucket()
    except S3Error:
        raise
