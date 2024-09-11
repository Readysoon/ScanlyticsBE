from fastapi import APIRouter, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr
from typing_extensions import Annotated
from surrealdb import Surreal

from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.user.userSchema import OrgaSignup, UserSignup, UserSimple

from .authService import check_mail_service, signup_service, login_service, get_current_user

from . import authSchema

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
    return await check_mail_service(
        user_email, 
        db
        )

# first user of a organization has to sign up for the organization too
@router.post("/orga_signup", response_model=authSchema.Token)
async def orga_signup(
    userin: OrgaSignup, 
    db: Surreal = Depends(get_db)
    ):
    return await signup_service(
        userin.user_email, 
        userin.user_name, 
        userin.user_password, 
        userin.user_role,
        userin.orga_address,
        userin.orga_email,
        userin.orga_name,
        db
        )

@router.post("/user_signuo", response_model=authSchema.Token)
async def user_signup(
    userin: UserSignup,
    db: Surreal = Depends(get_db)
    ):
    return await UserSignupService(
        userin.user_email, 
        userin.user_name, 
        userin.user_password, 
        userin.user_role,
        db
    )

# ordentliche Fehlermeldung zurückgeben und nicht nur out of index
@router.post("/login")
async def login(
    user_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    db: Surreal = Depends(get_db)
    ):
    return await login_service(
        db,
        user_data
        )

# get_current_user takes the token, extracts the id, looks with the id in the database and returns the user
# current_user saves everything from get_current_user
'''write proper errors when old jwt token was given'''
@router.post("/validate")
def validate(current_user = Depends(get_current_user)):
    return current_user





