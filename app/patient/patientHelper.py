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