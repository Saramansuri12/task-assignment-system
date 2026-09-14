from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User

from app.core.security import (
    decode_access_token,
)


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


# =========================================================
# CURRENT USER
# =========================================================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):

    payload = decode_access_token(token)

    if not payload:

        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    user_id = payload.get("sub")

    if not user_id:

        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token",
        )

    user = (
        db.query(User)
        .filter(
            User.user_id == int(user_id)
        )
        .first()
    )

    if not user or not user.is_active:

        raise HTTPException(
            status_code=401,
            detail="User is not active",
        )

    return user


# =========================================================
# ROLE CHECK
# =========================================================

def require_roles(*allowed_roles):

    def role_dependency(
        current_user: User = Depends(
            get_current_user
        ),
    ):

        if current_user.role not in allowed_roles:

            raise HTTPException(
                status_code=403,
                detail="Insufficient permissions",
            )

        return current_user

    return role_dependency