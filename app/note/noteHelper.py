from fastapi import status

from app.error.errorHelper import DatabaseErrorHelper 


async def GetNoteByIDHelper(note_id, current_user_id, db, error_stack):
    try:
        query_result = await db.query(
            f"SELECT * FROM PatientNote "
            f"WHERE id = PatientNote:{note_id};"
        )

        DatabaseErrorHelper(query_result, error_stack)
        
    except Exception as e: 
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                GetNoteByIDHelper
            ) 
    
    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_404_NOT_FOUND,
                "No Note found.",
                "None",
                GetNoteByIDHelper
            ) 

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
                GetNoteByIDHelper
            ) 
    
    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_403_FORBIDDEN,
                "You have no permission to view this note.",
                "None",
                GetNoteByIDHelper
            ) 
    
    result_without_status = query_result[0]['result'][0]

    return result_without_status