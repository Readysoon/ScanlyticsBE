from fastapi import APIRouter, Depends
from surrealdb import Surreal

'''added 2 "" for db.database for deployed mode'''
from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.auth.authService import get_current_user_id

from .patientService import CreatePatientService, GetPatientByID, UpdatePatientService, GetAllPatientsByUserID
from .patientSchema import CreatePatient


router = APIRouter(
    prefix="/patient",
    tags=["patient"],
)

@router.post("/")
async def create_patient(
    patientin: CreatePatient, 
    current_user_id = Depends(get_current_user_id),
    db: Surreal = Depends(get_db)
    ):
    return await CreatePatientService(patientin, current_user_id, db)

# rename this to something more checking if a patient is actually a user's
@router.get("/{patient_id}")
async def get_patient(
        patient_id: str,
        current_user_id = Depends(get_current_user_id),
        db: Surreal = Depends(get_db)
    ):
    return await GetPatientByID(patient_id, current_user_id, db)

@router.get("/")
async def get_all_patients(
        current_user_id = Depends(get_current_user_id),
        db: Surreal = Depends(get_db)
    ):
    return await GetAllPatientsByUserID(current_user_id, db)

@router.patch("/{patient_id}")
async def update_patient(
        patientin: CreatePatient,
        patient_id: str,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(get_current_user_id)
    ):
    return await UpdatePatientService(patientin, patient_id, current_user_id, db)