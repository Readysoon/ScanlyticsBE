from fastapi import APIRouter, Form, Depends
from pydantic.networks import EmailStr
from surrealdb import Surreal

from app.db.database import get_db
from app.user.userSchema import UserOrga, User

from .authService import CheckMailService, OrgaSignupService, LoginService, UserSignupService, GetCurrentUserIDHelper, ValidateService, UpdatePasswordService, VerificationService
from .authSchema import Login, Email, Password, Token


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
    return await CheckMailService(
            user_email, 
            db
        )

'''first user of a organization has to sign up for the organization too'''
@router.post("/orga_signup", response_model=Token)
async def orga_signup(
        user_in: UserOrga, 
        db: Surreal = Depends(get_db)
    ):
    return await OrgaSignupService(
            user_in,
            db
        )

@router.post("/user_signup", response_model=Token)
async def user_signup(
        user_in: User,
        db: Surreal = Depends(get_db)
    ):
    return await UserSignupService(
            user_in,
            db
        )

@router.post("/login")
async def login(
        user_data: Login, 
        db: Surreal = Depends(get_db)
    ):
    return await LoginService(
            user_data,
            db
        )

@router.patch("/password")
async def update_password(
        password: Password,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await UpdatePasswordService(
             password,
             current_user_id,
             db
        )

@router.post("/validate")
async def validate(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    return await ValidateService(
             current_user_id,
             db
        )

@router.get("/verify/{token}")
async def verify(
        token: str,
        db: Surreal = Depends(get_db)
    ):
    return await VerificationService(
             token,
             db
        )







