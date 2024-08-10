from fastapi import APIRouter, Form, Depends
from pydantic.networks import EmailStr
from surrealdb import Surreal

from db.database import get_db

from .authService import check_mail_service, signup_service

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


''', response_model=authSchema.Token'''
@router.post("/orga_signup" )
async def orga_signup(
    user_email: EmailStr = Form(...),
    user_name:  str = Form(...),
    user_password: str = Form(...),
    user_role: str = Form(...),

    orga_address: str = Form(...),
    orga_email: EmailStr = Form(...),
    orga_name: str = Form(...),

    db: Surreal = Depends(get_db)  # Use SurrealDB connection instead of SQLAlchemy session
    ):
    return await signup_service(user_email, user_name, user_password, user_role, orga_address, orga_email, orga_name, db)
