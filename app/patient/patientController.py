from fastapi import APIRouter, Depends

from db.database import get_db
from surrealdb import Surreal

from .patientService import CreatePatientService, UpdatePatientService, get_patient_by_id
from .patientSchema import CreatePatient

from auth.authService import get_current_user_id

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
    # print(patientin)
    # print(current_user_id)
    return await CreatePatientService(patientin, current_user_id, db)

@router.get("/get_patient_id/{patient_id}")
async def get_patient_id(
        patient_id: str,
        current_user_id = Depends(get_current_user_id),
        db: Surreal = Depends(get_db)
    ):
    return await get_patient_by_id(patient_id, current_user_id, db)

@router.patch("/update/{patient_id}")
async def update_patient(
    patient_id: str,
    patientin: CreatePatient,
    current_user_id = Depends(get_current_user_id),
    db: Surreal = Depends(get_db)
    ):
    return await UpdatePatientService(patientin, current_user_id, patient_id, db)
