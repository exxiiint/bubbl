from uuid import UUID

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.storage import StoredObject, save_media_record, storage


def upload_user_file(db: Session, owner_id: UUID, file: UploadFile, prefix: str) -> StoredObject:
    stored = storage.upload_file(file, owner_id, prefix)
    save_media_record(db, owner_id, stored)
    return stored
