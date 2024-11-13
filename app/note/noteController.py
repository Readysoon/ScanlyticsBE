from fastapi import APIRouter, Depends, Path
from surrealdb import Surreal
from typing import Annotated

from .noteSchema import Note
from .noteService import CreateNoteService, GetNoteByIDService, GetAllNotesByPatientIDService, UpdateNoteService, DeleteNoteService

from app.error.errorHelper import ErrorStack, RateLimit
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


router = APIRouter(
        prefix="/note",
        tags=["note"],
    )

@router.post("/{patient_id}")#, dependencies=[RateLimit.limiter()])
async def create_note(
        patient_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Patient ID must be 20 characters long and contain only alphanumeric characters"
                )],
        note_in: Note, 
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await CreateNoteService(
            patient_id,
            note_in, 
            current_user_id, 
            db,
            error_stack
        )
    

@router.get("/{note_id}")#, dependencies=[RateLimit.limiter()])
async def get_note(
        note_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Note ID must be 20 characters long and contain only alphanumeric characters"
                )],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetNoteByIDService(
            note_id, 
            current_user_id, 
            db,
            error_stack
        )


@router.get("/patient/{patient_id}")#, dependencies=[RateLimit.limiter()])
async def get_all_notes_by_patient_id(
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
    return await GetAllNotesByPatientIDService(
            patient_id,
            current_user_id, 
            db,
            error_stack
        )


@router.patch("/{note_id}")#, dependencies=[RateLimit.limiter()])
async def update_note(
        note_in: Note,
        note_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Note ID must be 20 characters long and contain only alphanumeric characters"
                )],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await UpdateNoteService(
            note_in, 
            note_id, 
            current_user_id, 
            db,
            error_stack
        )


@router.delete("/{note_id}")#, dependencies=[RateLimit.limiter()])
async def delete_note(
        note_id: Annotated[str, Path(
                min_length=20, 
                max_length=20,
                pattern=r'^[a-zA-Z0-9]+$',  
                description="Note ID must be 20 characters long and contain only alphanumeric characters"
                )],
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await DeleteNoteService(
            note_id,
            current_user_id,
            db,
            error_stack
        )

