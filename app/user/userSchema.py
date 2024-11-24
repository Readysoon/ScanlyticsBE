from pydantic import EmailStr

from app.auth.authSchema import Password, Email

'''question to Fabio: does this make sense or can i write it per class duplicate?'''

'''unused so far'''
class UserSimple(Password, Email):
    pass

class User(UserSimple):
    user_name: str
    user_role: str

class UserOrga(User):
    orga_address: str
    orga_email: EmailStr
    orga_name: str

