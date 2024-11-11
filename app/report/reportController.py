from fastapi import APIRouter, Depends, Path
from surrealdb import Surreal
from typing import Annotated


from .reportService import CreateReportService, GetReportByIDService, UpdateReportService, GetAllReportsByPatientIDService, DeleteReportService
from .reportSchema import Report

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


router = APIRouter(
    prefix="/report",
    tags=["report"],
)

'''TO DO: Create reports out of text and statement and patient data - '''
@router.post("/")
async def create_report(
        report_in: Report, 
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await CreateReportService(
            report_in,
            current_user_id, 
            db,
            error_stack
        )


@router.get("/{report_id}")
async def get_report(
        report_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Report ID must be 20 characters long and contain only alphanumeric characters"
                )],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetReportByIDService(
            report_id,
            current_user_id, 
            db,
            error_stack
        )


'''update to handle the new schema'''
@router.patch("/{report_id}")
async def update_report(
        report_in: Report,
        report_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Report ID must be 20 characters long and contain only alphanumeric characters"
                )],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await UpdateReportService(
            report_in,
            report_id, 
            current_user_id, 
            db,
            error_stack
        )


@router.get("/patient/{patient_id}")
async def get_all_reports_by_patient_and_user(
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
    return await GetAllReportsByPatientIDService(
            patient_id,
            current_user_id, 
            db,
            error_stack
        )


@router.delete("/{report_id}")
async def delete_patient(
        report_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Report ID must be 20 characters long and contain only alphanumeric characters"
                )],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db),
    ):
    error_stack = ErrorStack()
    return await DeleteReportService(
            report_id,
            current_user_id,
            db,
            error_stack
        )
