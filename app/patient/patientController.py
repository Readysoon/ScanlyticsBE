from surrealdb import Surreal
from fastapi import APIRouter, Depends
from typing import Annotated
from fastapi import Path

from .patientService import CreatePatientService, GetPatientByIDService, UpdatePatientService, GetAllPatientsByUserIDService, DeletePatientService
from .patientSchema import CreatePatient

from app.error.errorHelper import ErrorStack, RateLimit
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


router = APIRouter(
        prefix="/patient",
        tags=["patient"],
    )

@router.post("/", dependencies=[RateLimit.limiter()])
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


@router.get("/{patient_id}", dependencies=[RateLimit.limiter()])
async def get_patient(
        patient_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Patient ID must be 20 characters long and contain only alphanumeric characters"
                )],
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


@router.get("/", dependencies=[RateLimit.limiter()])
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


@router.patch("/{patient_id}", dependencies=[RateLimit.limiter()])
async def update_patient(
        patient_in: CreatePatient,
        patient_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Patient ID must be 20 characters long and contain only alphanumeric characters"
                )],
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


@router.delete("/{patient_id}", dependencies=[RateLimit.limiter()])
async def delete_patient(
        patient_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Patient ID must be 20 characters long and contain only alphanumeric characters"
                )],
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

