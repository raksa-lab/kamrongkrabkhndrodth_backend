from pathlib import Path
from fastapi import Depends, FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api import admin_books, auth, books, hero_slides, uploads
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine, get_db
from app.models.admin_user import AdminUser
from app.models.uploaded_file import UploadedFile

settings = get_settings()
app = FastAPI(title="Readwell Book Store API", version="0.1.0")
cors_origins = settings.cors_origins_list
allow_wildcard = "*" in cors_origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if allow_wildcard else cors_origins,
    allow_credentials=not allow_wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)

@app.get("/uploads/{filename}")
def serve_upload(filename: str, db: Session = Depends(get_db)):
    """Serve uploaded images directly from PostgreSQL (ensuring persistence on Render), with disk fallback."""
    # 1. Persistent PostgreSQL database lookup
    record = db.query(UploadedFile).filter(UploadedFile.filename == filename).first()
    if record and record.data:
        return Response(
            content=record.data,
            media_type=record.content_type or "image/jpeg",
            headers={
                "Cache-Control": "public, max-age=31536000, immutable",
                "Content-Disposition": f'inline; filename="{filename}"',
            },
        )

    # 2. Local disk fallback
    disk_path = Path(settings.upload_dir) / filename
    if disk_path.is_file():
        return FileResponse(disk_path)

    raise HTTPException(status_code=404, detail="File not found")

app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin_books.router)
app.include_router(uploads.router)
app.include_router(hero_slides.public_router)
app.include_router(hero_slides.admin_router)

@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(AdminUser).filter(AdminUser.email == settings.admin_email).first():
            db.add(AdminUser(email=settings.admin_email, password_hash=hash_password(settings.admin_password)))
            db.commit()

        # Preserve any existing disk files by syncing them into PostgreSQL
        upload_path = Path(settings.upload_dir)
        if upload_path.exists():
            for f in upload_path.iterdir():
                if f.is_file() and f.suffix.lower() in [".jpg", ".jpeg", ".png", ".webp"]:
                    if not db.query(UploadedFile).filter(UploadedFile.filename == f.name).first():
                        ext = f.suffix.lower()
                        ct = "image/jpeg" if ext in [".jpg", ".jpeg"] else ("image/png" if ext == ".png" else "image/webp")
                        try:
                            db.add(UploadedFile(filename=f.name, content_type=ct, data=f.read_bytes()))
                            db.commit()
                        except Exception:
                            db.rollback()
    finally:
        db.close()

@app.get("/")
def root():
    return {
        "status": "online",
        "service": "Readwell Book Store API",
        "docs": "/docs",
        "health": "/api/health",
    }

@app.get("/api/health")
def health():
    return {"status": "ok"}
