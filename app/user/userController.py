from fastapi import APIRouter

from .userService import CreateUserService

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/create")
async def create_user():
    result = await CreateUserService()
    return result