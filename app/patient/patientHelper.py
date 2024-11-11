from fastapi import status

from app.error.errorHelper import DatabaseErrorHelper 


async def GetAllPatientsByUserIDHelper(current_user_id, db, error_stack):
        try: 
            query_result = await db.query(
                    f"SELECT * FROM "
                    f"Treated_By WHERE "
                    f"out = {current_user_id};"
                )
            DatabaseErrorHelper(query_result, error_stack)
   
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetAllPatientsByUserIDHelper
                ) 
        
        try:
        
            patient_list = query_result[0]['result']

            return patient_list
        
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Result generation error.",
                    e,
                    GetAllPatientsByUserIDHelper
                ) 
            
            
async def GetPatientByIDHelper(patient_id, current_user_id, db, error_stack):
    try: 
        query_result = await db.query(
            """
            SELECT * 
            FROM Treated_By 
            WHERE out = $user_id;
            """,
            {
                "user_id": current_user_id
            }
        )
        DatabaseErrorHelper(query_result, error_stack)
        
    except Exception as e: 
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                GetPatientByIDHelper
            ) 
    
    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_404_NOT_FOUND,
                f"Patient not found under ID '{patient_id}'.",
                "Null",
                GetPatientByIDHelper
            ) 

    try: 
        query_result = await db.query(
            """
            SELECT * 
            FROM (
                SELECT * 
                FROM Treated_By 
                WHERE in = $patient_id 
                AND out = $user_id
            ).in;
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
                GetPatientByIDHelper
            ) 
    
    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_403_FORBIDDEN,
                "You have to permission to view this patient.",
                "Null",
                GetPatientByIDHelper
            ) 
    
    result_without_status = query_result[0]['result']

    return result_without_status