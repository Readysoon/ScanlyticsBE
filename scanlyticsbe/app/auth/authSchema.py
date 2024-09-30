from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class Password(BaseModel):
    password: str

class Login(BaseModel):
    user_email: str
    user_password: str
