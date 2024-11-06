from surrealdb import Surreal
from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from .patientService import CreatePatientService, GetPatientByIDService, UpdatePatientService, GetAllPatientsByUserIDService, DeletePatientService
from .patientSchema import CreatePatient

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


router = APIRouter(
        prefix="/patient",
        tags=["patient"],
    )

@router.post("/")
async def create_patient(
        patient_in: CreatePatient, 
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await CreatePatientService(
            patient_in, 
            current_user_id, 
            db, 
            error_stack
        )


@router.get("/{patient_id}")
async def get_patient(
        patient_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetPatientByIDService(
            patient_id, 
            current_user_id, 
            db,
            error_stack
        )


@router.get("/")
async def get_all_patients(
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetAllPatientsByUserIDService(
            current_user_id, 
            db, 
            error_stack
        )


@router.patch("/{patient_id}")
async def update_patient(
        patient_in: CreatePatient,
        patient_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await UpdatePatientService(
            patient_in, 
            patient_id, 
            current_user_id, 
            db, 
            error_stack
        )


@router.delete("/{patient_id}")
async def delete_patient(
        patient_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await DeletePatientService(
            patient_id,
            current_user_id,
            db,
            error_stack
        )

