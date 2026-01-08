from datetime import datetime
import re
from uuid import UUID
from pydantic import BaseModel, EmailStr, model_validator


class UserSignupRequest(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    password: str

    @model_validator(mode="after")
    def check_password(self):
        password = self.password

        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        if not re.search(r"[A-Z]", password):
            raise ValueError("Password must contain at least one uppercase letter")

        if not re.search(r"[a-z]", password):
            raise ValueError("Password must contain at least one lowercase letter")

        if not re.search(r"\d", password):
            raise ValueError("Password must contain at least one digit")

        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValueError("Password must contain at least one special character")

        return self


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
