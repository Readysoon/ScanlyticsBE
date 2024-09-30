from fastapi import APIRouter, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr
from typing_extensions import Annotated
from surrealdb import Surreal

from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.user.userSchema import OrgaSignup, User

from .authService import CheckMailService, OrgaSignupService, LoginService, UserSignupService

from .authSchema import Login, Token


'''	1.	Login
	2.	Logout
	3.	Register/Signup
	4.	Password reset
	5.	Email verification
	6.	Two-factor authentication
	7.	OAuth/Social login
	8.	Refresh token
'''

router = APIRouter(
            prefix="/auth",
            tags=["auth"],
        )

# first check if the mail is already in the database before entering all the other information
@router.post("/check_mail")
async def check_mail(
        user_email: EmailStr = Form(...),
        db: Surreal = Depends(get_db)
    ):
    return await CheckMailService(
            user_email, 
            db
        )

# first user of a organization has to sign up for the organization too
@router.post("/orga_signup", response_model=Token)
async def orga_signup(
        userin: OrgaSignup, 
        db: Surreal = Depends(get_db)
    ):
    return await OrgaSignupService(
            userin.user_email, 
            userin.user_name, 
            userin.user_password, 
            userin.user_role,
            userin.orga_address,
            userin.orga_email,
            userin.orga_name,
            db
        )

@router.post("/user_signup", response_model=Token)
async def user_signup(
        userin: User,
        db: Surreal = Depends(get_db)
    ):
    return await UserSignupService(
            userin.user_email, 
            userin.user_name, 
            userin.user_password, 
            userin.user_role,
            db
        )

@router.post("/login")
async def login(
        user_data: Login, 
        db: Surreal = Depends(get_db)
    ):
    return await LoginService(
            db,
            user_data
        )








