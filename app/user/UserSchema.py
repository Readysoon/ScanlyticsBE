from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    user_email: EmailStr
    user_name: str
    user_password: str
    user_role: str
    orga_address: str
    orga_email: EmailStr
    orga_name: str

class UserIn(BaseModel):
    user_email: EmailStr
    user_password: str