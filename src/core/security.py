"""JWT authentication utilities for DocSimplify."""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from jose import JWTError, jwt

from src.config.settings import AuthSettings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(user_id: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=AuthSettings.EXPIRE_MINUTES)
    payload = {"sub": user_id, "exp": expire}
    return jwt.encode(payload, AuthSettings.SECRET_KEY, algorithm=AuthSettings.ALGORITHM)


def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, AuthSettings.SECRET_KEY, algorithms=[AuthSettings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None
