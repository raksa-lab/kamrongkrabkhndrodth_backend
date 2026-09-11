from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.core.security import decode_token
from app.db.session import get_db
from app.models.admin_user import AdminUser

bearer = HTTPBearer()

def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> AdminUser:
    try:
        email = decode_token(credentials.credentials).get("sub")
    except Exception as exc:
        raise HTTPException(status_code=401, detail="Invalid token") from exc
    user = db.query(AdminUser).filter(AdminUser.email == email, AdminUser.is_active.is_(True)).first()
    if not user:
        raise HTTPException(status_code=401, detail="Admin account not found")
    return user
