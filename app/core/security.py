from datetime import datetime, timedelta, timezone
import jwt
from pwdlib import PasswordHash
from app.core.config import get_settings

password_hash = PasswordHash.recommended()

def hash_password(value: str) -> str:
    return password_hash.hash(value)

def verify_password(value: str, hashed: str) -> bool:
    return password_hash.verify(value, hashed)

def create_token(subject: str, expire_hours: int = 8) -> str:
    """Create a signed JWT token valid for exactly 8 hours (480 minutes)."""
    settings = get_settings()
    expire_minutes = settings.jwt_expire_minutes if settings.jwt_expire_minutes > 0 else (expire_hours * 60)
    expire_time = datetime.now(timezone.utc) + timedelta(minutes=expire_minutes)
    payload = {
        "sub": subject,
        "iat": datetime.now(timezone.utc),
        "exp": expire_time,
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

def decode_token(token: str) -> dict:
    return jwt.decode(token, get_settings().jwt_secret, algorithms=["HS256"])
