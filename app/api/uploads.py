import json
from io import BytesIO
from pathlib import Path
from uuid import uuid4
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
import httpx
from app.api.dependencies import get_current_admin
from app.core.config import get_settings

router = APIRouter(prefix="/api/admin", tags=["uploads"], dependencies=[Depends(get_current_admin)])
ALLOWED = {"image/jpeg": ".jpg", "image/png": ".png", "image/webp": ".webp"}


def ensure_bucket_public(minio_client, bucket_name: str):
    """Ensure the MinIO bucket exists and has public read access for storefront images."""
    if not minio_client.bucket_exists(bucket_name):
        minio_client.make_bucket(bucket_name)

    public_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"AWS": ["*"]},
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            }
        ],
    }
    try:
        minio_client.set_bucket_policy(bucket_name, json.dumps(public_policy))
    except Exception:
        # Ignore if policy is already managed by admin
        pass


@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(status_code=415, detail="Only JPEG, PNG, and WebP images are supported")
    
    settings = get_settings()
    filename = f"{uuid4().hex}{ALLOWED[file.content_type]}"
    content = await file.read()

    # 1. Primary Cloud Storage: MinIO
    if settings.minio_endpoint and settings.minio_access_key and settings.minio_secret_key:
        try:
            from minio import Minio

            minio_client = Minio(
                endpoint=settings.minio_endpoint,
                access_key=settings.minio_access_key,
                secret_key=settings.minio_secret_key,
                secure=settings.minio_secure,
            )

            # Ensure bucket exists and has public read permission
            ensure_bucket_public(minio_client, settings.minio_bucket)

            # Upload the file
            minio_client.put_object(
                bucket_name=settings.minio_bucket,
                object_name=filename,
                data=BytesIO(content),
                length=len(content),
                content_type=file.content_type,
            )

            # Build public URL
            if settings.minio_public_url:
                public_base = settings.minio_public_url.rstrip("/")
            else:
                scheme = "https" if settings.minio_secure else "http"
                public_base = f"{scheme}://{settings.minio_endpoint}"

            public_url = f"{public_base}/{settings.minio_bucket}/{filename}"
            return {"url": public_url, "filename": filename}
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload image to MinIO: {str(e)}"
            )

    # 2. Secondary Cloud Storage: Supabase Storage
    if settings.supabase_url and settings.supabase_service_key:
        upload_endpoint = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/{settings.supabase_bucket}/{filename}"
        headers = {
            "Authorization": f"Bearer {settings.supabase_service_key}",
            "apiKey": settings.supabase_service_key,
            "Content-Type": file.content_type,
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(upload_endpoint, content=content, headers=headers)
            if resp.status_code not in (200, 201):
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload to Supabase Storage: {resp.text}"
                )
        
        public_url = f"{settings.supabase_url.rstrip('/')}/storage/v1/object/public/{settings.supabase_bucket}/{filename}"
        return {"url": public_url, "filename": filename}

    # 3. Local Storage Fallback (for offline development)
    directory = Path(settings.upload_dir)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / filename).write_bytes(content)
    return {"url": f"/uploads/{filename}", "filename": filename}
