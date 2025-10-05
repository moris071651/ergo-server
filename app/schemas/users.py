import uuid
from pydantic import BaseModel, EmailStr

class UserSignupRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserAuthResponse(BaseModel):
    id: uuid.UUID
    username: str
    email: EmailStr
