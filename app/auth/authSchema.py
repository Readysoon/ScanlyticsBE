from pydantic import BaseModel, EmailStr

class Token(BaseModel):
    access_token: str
    token_type: str

class Password(BaseModel):
    user_password: str

class Email(BaseModel):
    user_email: EmailStr

class Login(Email, Password):
    pass
