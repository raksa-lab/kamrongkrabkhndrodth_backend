from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import get_settings

password_hash = PasswordHash.recommended()

def hash_password(value: str) -> str:
    return password_hash.hash(value)

def verify_password(value: str, hashed: str) -> bool:
    return password_hash.verify(value, hashed)

def create_token(subject: str) -> str:
    settings = get_settings()
    payload = {"sub": subject, "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)}
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
