from fastapi import APIRouter, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr
from typing_extensions import Annotated

from db.database import get_db
from surrealdb import Surreal

from .authService import check_mail_service, signup_service, login_service, get_current_user

from . import authSchema
from user.UserSchema import UserSignup, UserSimple

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

@router.post("/orga_signup", response_model=authSchema.Token)
async def orga_signup(
    userin: UserSignup, 
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

# , response_model=authSchema.Token
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
@router.post("/validate")
def validate(current_user = Depends(get_current_user)):
    return current_user





