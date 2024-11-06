from fastapi import status
from starlette.responses import JSONResponse

from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 
from app.auth.authHelper import ReturnAccessTokenHelper

'''
# Suggested:
status.HTTP_201_CREATED  # for successful creation
status.HTTP_404_NOT_FOUND  # if patient doesn't exist
status.HTTP_403_FORBIDDEN  # if user doesn't have permission to create notes for this patient
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid note data
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def CreateNoteService(patient_id, note_in, current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                f"Create PatientNote "
                f"Set symptoms = '{note_in.symptoms}', "
                f"diagnosis = '{note_in.diagnosis}', "
                f"treatment = '{note_in.treatment}', "
                f"severity = '{note_in.severity}', "
                f"is_urgent = {note_in.is_urgent}, "
                f"patient = 'Patient:{patient_id}', "
                f"user_owner = '{current_user_id}';"
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
status.HTTP_200_OK  # for successful retrieval
status.HTTP_404_NOT_FOUND  # when note doesn't exist (change from 500)
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to access the note
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetNoteByID(note_id, current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                f"SELECT * FROM PatientNote "
                f"WHERE id = PatientNote:{note_id} "
                f"AND user_owner = {current_user_id};"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetNoteByID
                ) 
        
        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "No Note found.",
                    "None",
                    GetNoteByID
                ) 
        
        result_without_status = query_result[0]['result']


        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Fetched note."
                    }, 
                    result_without_status,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(GetNoteByID, e, error_stack)

'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval (even with empty array)
status.HTTP_404_NOT_FOUND  # if patient doesn't exist
status.HTTP_403_FORBIDDEN  # if user doesn't have permission to view patient's notes
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetAllNotesByPatientID(patient_id, current_user_id, db, error_stack):
    try:
        try:
            query_result = await db.query(
                f"SELECT * FROM PatientNote "
                f"WHERE patient = Patient:{patient_id} "
                f"AND user_owner = {current_user_id};"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetNoteByID
                ) 
        
        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "No Note was found for this patient.",
                    "None",
                    GetNoteByID
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
        ExceptionHelper(GetNoteByID, e, error_stack)


'''find a solution for updating parameter "patient" properly, maybe doctor just has to delete it?'''
'''Works - except for when wrong parameter was given'''
'''
# Suggested:
status.HTTP_200_OK  # for successful update
status.HTTP_404_NOT_FOUND  # when note doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to update
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def UpdateNoteService(note_in, note_id, current_user_id, db, error_stack):
    try:
        try:
            symptoms = note_in.symptoms
            diagnosis = note_in.diagnosis
            treatment = note_in.treatment
            severity = note_in.severity
            is_urgent = note_in.is_urgent
            patient = note_in.patient
            set_string = "SET "

            # elongate the update_string
            if symptoms:
                set_string += f"symptoms = '{symptoms}', "
            if diagnosis:
                set_string += f"diagnosis = '{diagnosis}', "
            if treatment:
                set_string += f"treatment = '{treatment}', "
            if severity:
                set_string += f"severity = '{severity}', "
            if is_urgent:
                set_string += f"is_urgent = '{is_urgent}', "
            if patient:
                set_string += f"patient = '{patient}', "
            
            set_string = set_string[:-2]

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Set-string creation failed.",
                    e,
                    UpdateNoteService
                ) 
        
        try:
            # and finally put everything together and send it
            query_result = await db.query(
                    f"UPDATE ("
                    f"SELECT * FROM PatientNote "
                    f"WHERE id = 'PatientNote:{note_id}' "
                    f"AND user_owner = {current_user_id}"
                    f") {set_string};"
                )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
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
status.HTTP_204_NO_CONTENT  # for successful deletion
status.HTTP_404_NOT_FOUND  # when note doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to delete
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
''' 
async def DeleteNoteService(note_id, current_user_id, db, error_stack):
    try:
        # try:
        #     # search before deletion
        # except: 
        #     raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        try:
            query_result = await db.query(
                f"DELETE ("
                f"SELECT * FROM PatientNote "
                f"WHERE id = PatientNote:{note_id} "
                f"AND user_owner = {current_user_id})"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    DeleteNoteService
                ) 
            
        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Deleted note '{note_id}'."
                    }, 
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(DeleteNoteService, e, error_stack)


