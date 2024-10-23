from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

DATABASE_URL = os.getenv("SURREALDB_URL")
if DATABASE_URL == "ws://surrealdb:8000/rpc":
    REDIRECT_URL = "http://0.0.0.0:8000"
else: REDIRECT_URL = f"https{DATABASE_URL[3:-3]}"

router = APIRouter(
    prefix="/surrealdb",
    tags=["surreal"],
)

# in case you got "Connection header did not include 'upgrade'" you left the "/rpc" in the end
@router.get("/")
async def surrealdb_handler():
    print(DATABASE_URL)
    return RedirectResponse(url=REDIRECT_URL)