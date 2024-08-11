from fastapi import APIRouter, Form, Depends
from pydantic.networks import EmailStr
from surrealdb import Surreal

from db.database import get_db

from .authService import check_mail_service, signup_service

from .authSchema import Token
from app.user.UserSchema import UserIn

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
    return await check_mail_service(user_email, db)


# Use SurrealDB connection instead of SQLAlchemy session
''', response_model=authSchema.Token'''
@router.post("/orga_signup")
async def orga_signup(userin: UserIn, db: Surreal = Depends(get_db)):
    return await signup_service(
        userin.user_email, 
        userin.user_name, 
        userin.user_password, 
        userin.user_role, 
        userin.orga_address, 
        userin.orga_email, 
        userin.orga_name, 
        db)
