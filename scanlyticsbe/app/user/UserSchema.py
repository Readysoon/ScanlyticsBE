from pydantic import BaseModel, EmailStr

'''unused so far'''
'''question to Fabio: does this make sense or can i write it per class duplicate?'''
class UserSimple(BaseModel):
    user_email: EmailStr
    user_password: str

class User(UserSimple):
    user_name: str
    user_role: str

class UserOrga(User):
    orga_address: str
    orga_email: EmailStr
    orga_name: str

