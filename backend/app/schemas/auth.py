from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):

    username: str
    email: str
    password: str
    role: str = "EMPLOYEE"


class LoginRequest(BaseModel):

    username: str
    password: str


class TokenResponse(BaseModel):

    access_token: str
    token_type: str


class UserResponse(BaseModel):

    user_id: int
    username: str
    email: str
    role: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)