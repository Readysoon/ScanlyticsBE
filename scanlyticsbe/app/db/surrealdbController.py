from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

DATABASE_URL = os.getenv("SURREALDB_URL")
DATABASE_URL = DATABASE_URL[5:]

print(DATABASE_URL)


# alt: https://surrealdb-deployment-floral-meadow-3035.fly.dev

router = APIRouter(
    prefix="/surrealdb",
    tags=["surreal"],
)

@router.get("/")
async def surrealdb_handler():
    print("test")
    return RedirectResponse(url=f"https://surrealdb-deployment-floral-meadow-3035.fly.dev")