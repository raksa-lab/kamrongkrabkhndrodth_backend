from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from app.api.dependencies import get_current_admin
from app.core.config import get_settings

router = APIRouter(prefix="/api/admin", tags=["uploads"], dependencies=[Depends(get_current_admin)])
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP images are supported")
    directory = Path(get_settings().upload_dir)
    directory.mkdir(parents=True, exist_ok=True)
    name = f"{uuid4().hex}{ALLOWED[file.content_type]}"
    (directory / name).write_bytes(await file.read())
    return {"url": f"/uploads/{name}", "filename": name}
