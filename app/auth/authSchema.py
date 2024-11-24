from pydantic import BaseModel, EmailStr, Field
from typing import Annotated


class Password(BaseModel):
    user_password: Annotated[str, Field(min_length=8, max_length=25)]

class Email(BaseModel):
    user_email: EmailStr

class Login(Email, Password):
    pass

class SafeID(BaseModel):
    database_id: Annotated[str, Field(min_length=20, max_length=20)]
