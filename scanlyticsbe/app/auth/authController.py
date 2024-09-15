from fastapi import APIRouter, Form, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic.networks import EmailStr
from typing_extensions import Annotated
from surrealdb import Surreal

from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.user.userSchema import OrgaSignup, User, UserSimple
from scanlyticsbe.app.auth.authSchema import Password

from .authService import CheckMailService, OrgaSignupService, LoginService, GetCurrentUserService, UserSignupService, PatchUserService, DeleteUserService

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
    return await CheckMailService(
            user_email, 
            db
        )

# first user of a organization has to sign up for the organization too
@router.post("/orga_signup", response_model=authSchema.Token)
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

@router.post("/user_signup", response_model=authSchema.Token)
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
        user_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
        db: Surreal = Depends(get_db)
    ):
    return await LoginService(
            db,
            user_data
        )

@router.patch("/")
async def patch_user(
        userin: User,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(GetCurrentUserService)
    ):
    return await PatchUserService(
            userin, 
            current_user_id, 
            db
        )

@router.delete("/")
async def delete_user(
        password: Password, 
        current_user = Depends(GetCurrentUserService),
        db: Surreal = Depends(get_db)
    ):
    return await DeleteUserService(   
            password,  
            current_user,
            db
        )

# get_current_user takes the token, extracts the id, looks with the id in the database and returns the user
# current_user saves everything from get_current_user
'''write proper errors when old jwt token was given'''
@router.get("/validate")
def validate(
        current_user = Depends(GetCurrentUserService)
    ):
    return current_user





