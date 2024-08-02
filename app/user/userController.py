from fastapi import APIRouter

from .userService import CreateUserService

router = APIRouter(
    prefix="/user",
    tags=["user"],
)

@router.get("/create")
async def create_user():
    print("hello from fastapi")
    result = await CreateUserService()
    return result