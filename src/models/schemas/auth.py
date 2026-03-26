from pydantic import Field
from src.models.schemas.base import ApiModel


class UserCreate(ApiModel):
    email: str
    password: str = Field(min_length=6)
    name: str = Field(min_length=1)


class UserLogin(ApiModel):
    email: str
    password: str


class AuthUser(ApiModel):
    user_id: str = Field(alias="userId")
    email: str
    name: str


class AuthResponse(ApiModel):
    token: str
    user_id: str = Field(alias="userId")
    user: AuthUser
