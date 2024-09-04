from fastapi import APIRouter, Depends
from surrealdb import Surreal

'''added 2 "" for db.database for deployed mode'''
from scanlyticsbe.app.db.database import get_db
from scanlyticsbe.app.auth.authService import get_current_user_id

from .patientService import CreatePatientService, get_patient_by_id, UpdatePatientService
from .patientSchema import CreatePatient


router = APIRouter(
    prefix="/patient",
    tags=["patient"],
)

@router.post("/create")
async def create_patient(
    patientin: CreatePatient, 
    current_user_id = Depends(get_current_user_id),
    db: Surreal = Depends(get_db)
    ):
    print(patientin)
    print(current_user_id)
    return await CreatePatientService(patientin, current_user_id, db)

# missing: get all patients of a specific user

# rename this to something more checking if a patient is actually a user's
@router.get("/get/{patient_id}")
async def get_patient_id(
        patient_id: str,
        current_user_id = Depends(get_current_user_id),
        db: Surreal = Depends(get_db)
    ):
    print("hello from the GET route")
    return await get_patient_by_id(patient_id, current_user_id, db)

@router.patch("/update/{patient_id}")
async def update_patient(
        patientin: CreatePatient,
        patient_id: str,
        db: Surreal = Depends(get_db),
        current_user_id = Depends(get_current_user_id)
    ):
    return await UpdatePatientService(patientin, patient_id, current_user_id, db)

