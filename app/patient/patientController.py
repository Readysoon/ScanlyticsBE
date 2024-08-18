from fastapi import APIRouter, Depends

from db.database import get_db
from surrealdb import Surreal

from .patientService import CreatePatientService

from auth.authService import get_current_user

router = APIRouter(
    prefix="/patient",
    tags=["patient"],
)

@router.post("/create")
async def create_praxis(
    current_user = Depends(get_current_user),
    db: Surreal = Depends(get_db)
    ):
    print(current_user)
    # result = await CreatePraxisService()
    return current_user # result