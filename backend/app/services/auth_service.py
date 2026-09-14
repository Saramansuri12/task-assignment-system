from sqlalchemy.orm import Session

from app.db.models import User

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
)


class AuthService:

    def __init__(self, db: Session):

        self.db = db

    # =========================================================
    # CREATE USER
    # =========================================================

    def create_user(
        self,
        username: str,
        email: str,
        password: str,
        role: str = "EMPLOYEE",
    ):

        existing_username = (
            self.db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if existing_username:
            return None, "Username already exists"

        existing_email = (
            self.db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if existing_email:
            return None, "Email already exists"

        allowed_roles = {
            "ADMIN",
            "MANAGER",
            "EMPLOYEE",
        }

        role = role.upper()

        if role not in allowed_roles:
            return None, "Invalid role"

        user = User(
            username=username,
            email=email,
            password_hash=hash_password(
                password
            ),
            role=role,
            is_active=True,
        )

        self.db.add(user)

        try:

            self.db.commit()
            self.db.refresh(user)

        except Exception:

            self.db.rollback()
            raise

        return user, None

    # =========================================================
    # AUTHENTICATE
    # =========================================================

    def authenticate(
        self,
        username: str,
        password: str,
    ):

        user = (
            self.db.query(User)
            .filter(
                User.username == username
            )
            .first()
        )

        if not user:
            return None

        if not user.is_active:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user

    # =========================================================
    # LOGIN TOKEN
    # =========================================================

    def create_token(
        self,
        user: User,
    ):

        return create_access_token({
            "sub": str(user.user_id),
            "username": user.username,
            "role": user.role,
        })