from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db.models import User

from app.schemas.auth import (
    UserCreate,
    UserResponse,
    LoginRequest,
    TokenResponse,
)

from app.services.auth_service import (
    AuthService,
)

from app.api.dependencies import (
    get_current_user,
)


router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


# =========================================================
# REGISTER
# =========================================================

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=201,
)
def register(
    data: UserCreate,
    db: Session = Depends(get_db),
):

    service = AuthService(db)

    user, error = service.create_user(
        username=data.username,
        email=data.email,
        password=data.password,
        role=data.role,
    )

    if error:

        raise HTTPException(
            status_code=409,
            detail=error,
        )

    return user


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=TokenResponse,
)
def login(
    data: LoginRequest,
    db: Session = Depends(get_db),
):

    service = AuthService(db)

    user = service.authenticate(
        username=data.username,
        password=data.password,
    )

    if not user:

        raise HTTPException(
            status_code=401,
            detail="Invalid username or password",
            headers={
                "WWW-Authenticate": "Bearer"
            },
        )

    token = service.create_token(user)

    return {
        "access_token": token,
        "token_type": "bearer",
    }


# =========================================================
# CURRENT USER
# =========================================================

@router.get(
    "/me",
    response_model=UserResponse,
)
def current_user(
    user: User = Depends(
        get_current_user
    ),
):

    return user