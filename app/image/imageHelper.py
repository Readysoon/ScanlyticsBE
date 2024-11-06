from fastapi import status

from app.patient.patientHelper import GetAllPatientsByUserIDHelper

from app.error.errorHelper import DatabaseErrorHelper 

# 1. check if the patient exisits
# 2. check if the user has access to it


'''
# Suggested
status.HTTP_404_NOT_FOUND  # when no images found for patient - check
status.HTTP_403_FORBIDDEN  # when user doesn't have access to patient's images -check
status.HTTP_200_OK  # for successful retrieval (add this) - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors -check
'''
async def GetImagesByPatientHelper(patient_id, current_user_id, db, error_stack):
        
        # check if the patient exists
        try:
            query_result = await db.query(
                f"SELECT * FROM Patient "
                f"WHERE id = Patient:{patient_id};"
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetImagesByPatientHelper
                ) 
                    
        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_404_NOT_FOUND,
                    f"No patient was found for ID '{patient_id}'.",
                    "None",
                    GetImagesByPatientHelper
                ) 
            
        # check if the patient is users
            
        try:
            users_patient_list = await GetAllPatientsByUserIDHelper(current_user_id, db, error_stack)
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "GetAllPatientsByUserIDHelper",
                    e,
                    GetImagesByPatientHelper
                ) 
            
        patient_id_list = []
            
        for patient in users_patient_list:
            patient_id_list.append(patient['in'])
            
        if query_result[0]['result'][0]['id'] not in patient_id_list:
            error_stack.add_error(
                    status.HTTP_401_UNAUTHORIZED,
                    "You are not authorized to view this patients images.",
                    e,
                    GetImagesByPatientHelper
                )
            
        # retrieve Images
            
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
            
        if not query_result[0]['result'][0]:
             error_stack.add_error(
                    status.HTTP_404_NOT_FOUND,
                    f"No Image found for patient '{patient_id}'.",
                    "None",
                    GetImagesByPatientHelper
                )
        
        image_list = query_result[0]['result']
            
        return image_list

'''
#Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion
status.HTTP_404_NOT_FOUND  # when image not found - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to delete - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''

async def DeleteImageByIDHelper(image_id, current_user_id, db, error_stack):

    try: 
        query_result = await db.query(
                f"SELECT * FROM Image "
                f"WHERE id = 'Image:{image_id}';"
            )
        
        DatabaseErrorHelper(query_result, error_stack)

    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query 1 error.",
                e,
                DeleteImageByIDHelper
            )
    
    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Image not in database",
                "None",
                DeleteImageByIDHelper
            )
        
    try: 
        query_result = await db.query(
                f"SELECT * FROM Image "
                f"user = '{current_user_id}' "
                f"AND id = 'Image:{image_id}';"
            )
        
        DatabaseErrorHelper(query_result, error_stack)

    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Query 2 error.",
                e,
                DeleteImageByIDHelper
            )
    
    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "You are not authorized to delete this image",
                "None",
                DeleteImageByIDHelper
            )
        
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
        
    if not query_result[0]['result']:
        return True
    else: 
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Image was not deleted.",
                "None",
                DeleteImageByIDHelper
            )    
