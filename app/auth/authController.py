from fastapi import APIRouter, Depends
from surrealdb import Surreal

from .authSchema import Login, Email, Password, Token
from .authService import CheckMailService, OrgaSignupService, LoginService, UserSignupService, ValidateService, UpdatePasswordService, VerificationService

from app.user.userSchema import UserOrga, User
from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


'''	1.	Login - check
	2.	Logout - check
	3.	Register/Signup - check 
	4.	Password reset - check
	5.	Email verification - check (Mailchimp)
	6.	Two-factor authentication - oauth needed
	7.	OAuth/Social login - oauth needed
	8.	Refresh token - check
'''

router = APIRouter(
            prefix="/auth",
            tags=["auth"],
        )

@router.post("/check_mail")
async def check_mail(
        user_email: Email,
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await CheckMailService(
            user_email, 
            db,
            error_stack
        )


'''first user of a organization has to sign up for the organization too'''
@router.post("/orga_signup")
async def orga_signup(
        user_in: UserOrga, 
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await OrgaSignupService(
            user_in,
            db,
            error_stack
        )


@router.post("/user_signup")
async def user_signup(
        user_in: User,
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await UserSignupService(
            user_in,
            db,
            error_stack
        )


@router.post("/login")
async def login(
        user_data: Login, 
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await LoginService(
            user_data,
            db,
            error_stack
        )


@router.patch("/password")
async def update_password(
        password: Password,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = current_user_id
    return await UpdatePasswordService(
             password,
             current_user_id,
             db,
             error_stack
        )


@router.post("/validate")
async def validate(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await ValidateService(
             current_user_id,
             db,
             error_stack
        )


@router.get("/verify/{token}")
async def verify(
        token: str,
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await VerificationService(
             token,
             db,
             error_stack
        )








