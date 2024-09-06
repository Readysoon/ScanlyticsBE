from fastapi import APIRouter, Depends
from surrealdb import Surreal

from scanlyticsbe.app.seed.seedService import SeedUserService
from scanlyticsbe.app.auth.authSchema import Token
from scanlyticsbe.app.db.database import get_db


router = APIRouter(
    prefix="/seed",
    tags=["seed"],
)

@router.post("/orga_user", response_model=Token)
async def seed_user(db: Surreal = Depends(get_db)):
    return await SeedUserService(db)