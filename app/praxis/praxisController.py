from fastapi import APIRouter

from .praxisService import CreatePraxisService

router = APIRouter(
    prefix="/praxis",
    tags=["praxis"],
)

@router.get("/create")
async def create_praxis():
    result = await CreatePraxisService()
    return result