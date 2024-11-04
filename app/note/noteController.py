from fastapi import APIRouter, Depends
from surrealdb import Surreal

from app.note.noteSchema import Note
from app.note.noteService import CreateNoteService, GetNoteByID, GetAllNotesByPatientID, UpdateNoteService, DeleteNoteService

from app.error.errorHelper import ErrorStack
from app.auth.authHelper import GetCurrentUserIDHelper

from app.db.database import get_db


router = APIRouter(
        prefix="/note",
        tags=["note"],
    )

@router.post("/{patient_id}")
async def create_note(
        patient_id: str,
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

# rename this to something more checking if a patient is actually a user's
@router.get("/{note_id}")
async def get_note(
        note_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetNoteByID(
            note_id, 
            current_user_id, 
            db,
            error_stack
        )

@router.get("/patient/{patient_id}")
async def get_all_notes_by_patient_id(
        patient_id: str,
        current_user_id = Depends(GetCurrentUserIDHelper),
        db: Surreal = Depends(get_db)
    ):
    error_stack = ErrorStack()
    return await GetAllNotesByPatientID(
            patient_id,
            current_user_id, 
            db,
            error_stack
        )

@router.patch("/{note_id}")
async def update_note(
        note_in: Note,
        note_id: str,
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


@router.delete("/{note_id}")
async def delete_note(
        note_id: str,
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

