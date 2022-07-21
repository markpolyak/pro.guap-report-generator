from pydantic import BaseModel
from typing import Optional


class LoginPass(BaseModel):
    login: str
    password: str


class AuthForm(BaseModel):
    login_pass: Optional[LoginPass] = None
    user_cookie: Optional[str] = None

