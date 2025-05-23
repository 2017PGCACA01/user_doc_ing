from typing import Literal

from pydantic import BaseModel, EmailStr, constr

class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8)
    role: Literal["viewer", "editor", "admin"]

class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str

class UserResponseSchema(BaseModel):
    id: int
    email: EmailStr
    role: Literal["viewer", "editor", "admin"]
