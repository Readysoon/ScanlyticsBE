from fastapi import APIRouter, Form
from pydantic.networks import EmailStr


from . import authSchema
from . import authService


router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

@router.post("/signup", response_model=authSchema.Token)
async def signup(
    username: EmailStr = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    return await signup_service(db, username, password, first_name, last_name)
