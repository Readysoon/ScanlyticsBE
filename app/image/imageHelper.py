from fastapi import status

from app.error.errorHelper import DatabaseErrorHelper 


async def GetImagesByPatientHelper(patient_id, current_user_id, db, error_stack):
        try:
            query_result = await db.query(
                f"SELECT * FROM Image WHERE "
                f"user = '{current_user_id}' "
                f"AND patient = 'Patient:{patient_id}';"
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetImagesByPatientHelper
                ) 
            
        
        image_list = query_result[0]['result']
            
        return image_list


async def DeleteImageByIDHelper(image_id, current_user_id, db, error_stack):
    try: 
        query_result = await db.query(
                f"DELETE Image WHERE "
                f"user = '{current_user_id}' "
                f"AND id = 'Image:{image_id}';"
            )
        
        DatabaseErrorHelper(query_result, error_stack)

    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query error.",
                e,
                DeleteImageByIDHelper
            )
        
    if query_result[0] == '':
        return True
    else: 
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Image was not deleted.",
                "None",
                DeleteImageByIDHelper
            )    
