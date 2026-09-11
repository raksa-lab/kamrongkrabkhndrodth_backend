from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import admin_books, auth, books, uploads
from app.core.config import get_settings
from app.core.security import hash_password
from app.db.session import Base, SessionLocal, engine
from app.models.admin_user import AdminUser

settings = get_settings()
app = FastAPI(title="Readwell Book Store API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.include_router(auth.router)
app.include_router(books.router)
app.include_router(admin_books.router)
app.include_router(uploads.router)

@app.on_event("startup")
def initialize_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if not db.query(AdminUser).filter(AdminUser.email == settings.admin_email).first():
            db.add(AdminUser(email=settings.admin_email, password_hash=hash_password(settings.admin_password)))
            db.commit()
    finally:
        db.close()

@app.get("/api/health")
def health():
    return {"status": "ok"}
