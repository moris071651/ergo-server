from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr


class UserSignupRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserAuthResponse(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr


class AuthSessionInfo(BaseModel):
    user_id: UUID
    issued_at: datetime
    expires_at: datetime
    jti: UUID
