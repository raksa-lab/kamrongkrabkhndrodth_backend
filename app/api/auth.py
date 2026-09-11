from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.security import create_token, verify_password
from app.db.session import get_db
from app.models.admin_user import AdminUser
from app.schemas.auth import LoginRequest, TokenResponse

router = APIRouter(prefix="/api/admin", tags=["admin-auth"])

@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(AdminUser).filter(AdminUser.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return TokenResponse(access_token=create_token(user.email))
