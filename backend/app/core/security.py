from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


# =========================================================
# PASSWORD
# =========================================================

def hash_password(password: str) -> str:
    password_bytes = password.encode("utf-8")

    if len(password_bytes) > 72:
        raise ValueError(
            "Password cannot be longer than 72 bytes"
        )

    return bcrypt.hashpw(
        password_bytes,
        bcrypt.gensalt(),
    ).decode("utf-8")


def verify_password(
    plain_password: str,
    hashed_password: str,
) -> bool:
    password_bytes = plain_password.encode("utf-8")

    if len(password_bytes) > 72:
        return False

    return bcrypt.checkpw(
        password_bytes,
        hashed_password.encode("utf-8"),
    )


# =========================================================
# JWT
# =========================================================

def create_access_token(
    data: dict,
    expires_minutes: int = 60,
) -> str:

    payload = data.copy()

    expire = (
        datetime.now(timezone.utc)
        + timedelta(
            minutes=expires_minutes
        )
    )

    payload.update({
        "exp": expire,
    })

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )


def decode_access_token(token: str):

    try:

        return jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[
                settings.JWT_ALGORITHM
            ],
        )

    except JWTError:

        return None