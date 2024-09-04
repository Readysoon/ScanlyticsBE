from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

DATABASE_URL = os.getenv("SURREALDB_URL")


router = APIRouter(
    prefix="/surrealdb",
    tags=["surreal"],
)

@router.get("/")
async def surrealdb_handler():
    print("test")
    return RedirectResponse(url=f"https{DATABASE_URL[5:]}")