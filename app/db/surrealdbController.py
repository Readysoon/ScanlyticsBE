from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(
    prefix="/surrealdb",
    tags=["surreal"],
)

@router.get("/")
async def surrealdb_handler():
    # Instead of returning the result, redirect to the desired URL
    print("test")
    return RedirectResponse(url="http://0.0.0.0:8000")