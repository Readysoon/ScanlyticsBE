from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

DATABASE_URL = os.getenv("SURREALDB_URL")
print(DATABASE_URL)
if DATABASE_URL == "ws://surrealdb:8000/rpc":
    DATABASE_URL = "http://0.0.0.0:8000"
# else: DATABASE_URL = f"wss{DATABASE_URL[5:]}/rpc"
print(DATABASE_URL)


router = APIRouter(
    prefix="/surrealdb",
    tags=["surreal"],
)

@router.get("/")
async def surrealdb_handler():
    print(DATABASE_URL)
    return RedirectResponse(url=DATABASE_URL)