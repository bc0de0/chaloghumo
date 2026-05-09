import os
import re
import unicodedata

from fastapi import HTTPException, UploadFile

MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".pdf"}
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "application/pdf"}


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename to prevent directory traversal and other attacks.
    """
    # 1. Normalize unicode
    filename = unicodedata.normalize("NFKC", filename)
    # 2. Keep only alphanumeric, dots, and underscores
    filename = re.sub(r"[^\w\d.\-]", "_", filename)
    # 3. Prevent hidden files or directory traversal
    filename = filename.lstrip(".")
    return filename


async def validate_upload(file: UploadFile):
    """
    Perform security validations on uploaded files.
    """
    # 1. Check extension
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file extension.")

    # 2. Check MIME type
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type.")

    # 3. Check file size
    size = 0
    # Read in chunks to avoid memory spikes
    while chunk := await file.read(1024 * 100):
        size += len(chunk)
        if size > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, detail="File size exceeds limit (5MB)."
            )

    # Reset file pointer for subsequent reads
    await file.seek(0)

    return sanitize_filename(file.filename or "uploaded_file")
