from fastapi import APIRouter, Form, Depends
from pydantic.networks import EmailStr
from surrealdb import Surreal

from db.database import get_db

from . import authSchema
from . import authService

from .authService import signup_service


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)
# ''', response_model=authSchema.Token'''
@router.post("/signup" )
async def signup(
    username: EmailStr = Form(...),
    password: str = Form(...),
    # testwise hardcoded (uncomment above lines later):
    # username: "Hans",
    # password: "12234"
    db: Surreal = Depends(get_db)  # Use SurrealDB connection instead of SQLAlchemy session
    ):
    return await signup_service(username, password, db)
