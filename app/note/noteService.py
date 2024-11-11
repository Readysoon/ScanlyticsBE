from fastapi import status
from starlette.responses import JSONResponse

from .noteHelper import GetNoteByIDHelper

from app.patient.patientHelper import GetPatientByIDHelper
from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 
from app.auth.authHelper import ReturnAccessTokenHelper

'''
# Suggested:
status.HTTP_201_CREATED  # for successful creation - check 
status.HTTP_404_NOT_FOUND  # if patient doesn't exist - check (GetPatientByIDHelper)
status.HTTP_403_FORBIDDEN  # if user doesn't have permission to create notes for this patient - check (GetPatientByIDHelper)
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid note data - to be done in schema checking
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def CreateNoteService(patient_id, note_in, current_user_id, db, error_stack):
    try:
        patient = await GetPatientByIDHelper(patient_id, current_user_id, db, error_stack)

        try:
            query_result = await db.query(
                """
                CREATE PatientNote SET 
                    symptoms = $symptoms,
                    diagnosis = $diagnosis,
                    treatment = $treatment,
                    severity = $severity,
                    is_urgent = $is_urgent,
                    patient = $patient_id,
                    user_owner = $user_id;
                """,
                {
                    "symptoms": note_in.symptoms,
                    "diagnosis": note_in.diagnosis,
                    "treatment": note_in.treatment,
                    "severity": note_in.severity,
                    "is_urgent": note_in.is_urgent,
                    "patient_id": f"Patient:{patient_id}",
                    "user_id": current_user_id
                }
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    f"Query error: {query_result}",
                    e,
                    CreateNoteService
                ) 
        
        result_without_status = query_result[0]['result']

        return JSONResponse(
                status_code=201, 
                content=[
                    {
                        "message": f"Note created."
                    }, 
                    result_without_status,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(CreateNoteService, e, error_stack)

'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval - check 
status.HTTP_404_NOT_FOUND  # when note doesn't exist (change from 500) - check 
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to access the note - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetNoteByIDService(note_id, current_user_id, db, error_stack):
    try:
        note = await GetNoteByIDHelper(note_id, current_user_id, db, error_stack)

        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Fetched note."
                    }, 
                    note,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(GetNoteByIDService, e, error_stack)

'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval (even with empty array) - check
status.HTTP_404_NOT_FOUND  # if patient doesn't exist - check 
status.HTTP_403_FORBIDDEN  # if user doesn't have permission to view patient's notes -check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors -check
'''
async def GetAllNotesByPatientIDService(patient_id, current_user_id, db, error_stack):
    try:
        patient = await GetPatientByIDHelper(patient_id, current_user_id, db, error_stack)

        try:
            query_result = await db.query(
                """
                SELECT * 
                FROM PatientNote 
                WHERE patient = $patient_id 
                AND user_owner = $user_id;
                """,
                {
                    "patient_id": f"Patient:{patient_id}",
                    "user_id": current_user_id
                }
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetAllNotesByPatientIDService
                ) 
        
        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "No Note was found for this patient.",
                    "None",
                    GetAllNotesByPatientIDService
                ) 
        
        result_without_status = query_result[0]['result']

        note_count = 0

        for note in result_without_status:
            note_count += 1

        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Found {note_count} Note(s) for patient '{patient_id}'."
                    }, 
                    result_without_status,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(GetAllNotesByPatientIDService, e, error_stack)


'''find a solution for updating parameter "patient" properly, maybe doctor just has to delete it?'''
'''Works - except for when wrong parameter was given'''
'''
# Suggested:
status.HTTP_200_OK  # for successful update
status.HTTP_404_NOT_FOUND  # when note doesn't exist - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to update - check
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data - to be done in schemas
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def UpdateNoteService(note_in, note_id, current_user_id, db, error_stack):
    try:
        note = await GetNoteByIDHelper(note_id, current_user_id, db, error_stack)

        # Build update parameters and set parts dynamically
        update_params = {}
        set_parts = []

        if note_in.symptoms:
            set_parts.append("symptoms = $symptoms")
            update_params["symptoms"] = note_in.symptoms
        
        if note_in.diagnosis:
            set_parts.append("diagnosis = $diagnosis")
            update_params["diagnosis"] = note_in.diagnosis
        
        if note_in.treatment:
            set_parts.append("treatment = $treatment")
            update_params["treatment"] = note_in.treatment
        
        if note_in.severity:
            set_parts.append("severity = $severity")
            update_params["severity"] = note_in.severity
        
        if note_in.is_urgent:
            set_parts.append("is_urgent = $is_urgent")
            update_params["is_urgent"] = note_in.is_urgent
        
        if note_in.patient:
            set_parts.append("patient = $patient")
            update_params["patient"] = note_in.patient

        # Add the required WHERE clause parameters
        update_params.update({
            "note_id": f"PatientNote:{note_id}",
            "user_id": current_user_id
        })

        query_result = await db.query(
            f"""
            UPDATE (
                SELECT * 
                FROM PatientNote 
                WHERE id = $note_id 
                AND user_owner = $user_id
            ) SET {", ".join(set_parts)};
            """,
            update_params
        )

        DatabaseErrorHelper(query_result, error_stack)

    except Exception as e:
        error_stack.add_error(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "Update query failed.",
            e,
            UpdateNoteService
        )

        
        result_without_status = query_result[0]['result']

        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Updated note '{note_id}'."
                    }, 
                    result_without_status,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(UpdateNoteService, e, error_stack)
    
    
'''
# Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion - check
status.HTTP_404_NOT_FOUND  # when note doesn't exist - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to delete - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
''' 
async def DeleteNoteService(note_id, current_user_id, db, error_stack):
    try:
        note = await GetNoteByIDHelper(note_id, current_user_id, db, error_stack)

        try:
            query_result = await db.query(
                """
                DELETE (
                    SELECT * 
                    FROM PatientNote 
                    WHERE id = $note_id 
                    AND user_owner = $user_id
                );
                """,
                {
                    "note_id": f"PatientNote:{note_id}",
                    "user_id": current_user_id
                }
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    DeleteNoteService
                ) 
            
        if not query_result[0]['result']:
            return JSONResponse(
                    status_code=204, 
                    content=[
                        {
                            "message": f"Deleted note '{note_id}'."
                        }, 
                        ReturnAccessTokenHelper(current_user_id, error_stack)
                        ]
                    )
        else:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Deletion error.",
                    "None",
                    DeleteNoteService
                ) 
            
    except Exception as e:
        ExceptionHelper(DeleteNoteService, e, error_stack)


