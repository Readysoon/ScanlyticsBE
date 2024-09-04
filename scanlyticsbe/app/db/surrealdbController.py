from fastapi import APIRouter
from fastapi.responses import RedirectResponse


router = APIRouter(
    prefix="/surrealdb",
    tags=["surreal"],
)

@router.get("/")
async def surrealdb_handler():
    print("test")
    return RedirectResponse(url="https://surrealdb-deployment-floral-meadow-3035.fly.dev")