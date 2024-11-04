from fastapi import HTTPException, status

from app.auth.authService import ReturnAccessTokenHelper
from app.report.reportService import GetAllReportsByPatientIDService, DeleteReportService
from app.image.imageService import GetImagesByPatient, DeleteImageByID

from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 

'''
# Suggested:
status.HTTP_201_CREATED  # for successful creation
status.HTTP_400_BAD_REQUEST  # for invalid patient data
status.HTTP_409_CONFLICT  # if patient already exists
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def CreatePatientService(patientin, current_user_id, db, error_stack):
    try:
        try:
            # Create the Patient while relating it to the current_user then Select * from the just created patient (instead of returing the relation)
            query_result = await db.query(
                f"SELECT * FROM (("
                f"RELATE ("
                f"CREATE Patient "
                f"SET name = '{patientin.patient_name}', "
                f"date_of_birth = '{patientin.date_of_birth}', "
                f"gender = '{patientin.gender}', "
                f"contact_number = '{patientin.contact_number}', "
                f"address = '{patientin.address}'"
                f")->Treated_By->{current_user_id}"
                f").in)[0];"
            )

            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    CreatePatientService
                ) 
        
        result_without_status = query_result[0]['result']
        
        return ReturnAccessTokenHelper(current_user_id, error_stack), result_without_status
            
    except Exception as e:
        ExceptionHelper(CreatePatientService, error_stack, e)


# Looks with the patient_id and current_user_id which patients are to user 
# with the id and returns information about the patient
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval
status.HTTP_404_NOT_FOUND  # when patient doesn't exist (change from 500)
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to access patient
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetPatientByID(patient_id, current_user_id, db, error_stack):
    # Checking if patient is user's patient
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM ("
                f"SELECT * FROM "
                f"Treated_By WHERE "
                f"in = 'Patient:{patient_id}' "
                f"AND out = '{current_user_id}'"
                f").in;"
            )
            DatabaseErrorHelper(query_result, error_stack)
            
        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetPatientByID
                ) 
        
        if not query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "No record was found for this patient.",
                    "Null",
                    GetPatientByID
                ) 
        
        result_without_status = query_result[0]['result']
  
        return ReturnAccessTokenHelper(current_user_id, error_stack), result_without_status
    
    except Exception as e:
        ExceptionHelper(CreatePatientService, error_stack, e)

'''
# Suggested:
status.HTTP_200_OK  # for successful update
status.HTTP_404_NOT_FOUND  # when patient doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to update
status.HTTP_422_UNPROCESSABLE_ENTITY  # for invalid update data
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def UpdatePatientService(patientin, patient_id, current_user_id, db, error_stack):
        try:
            try:
                name = patientin.patient_name
                date_of_birth = patientin.date_of_birth
                gender = patientin.gender
                contact_number = patientin.contact_number
                address = patientin.address
                set_string = "SET "

                # elongate the update_string
                if name:
                    set_string += f"name = '{name}', "
                if date_of_birth:
                    set_string += f"date_of_birth = '{date_of_birth}', "
                if gender:
                    set_string += f"gender = '{gender}', "
                if contact_number:
                    set_string += f"contact_number = '{contact_number}', "
                if address:
                    set_string += f"address = '{address}', "
                
                set_string = set_string[:-2]

            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Set-string creation failed",
                    e,
                    UpdatePatientService
                ) 

            try: 
                # and finally put everything together and send it
                query_result = await db.query(
                        f"UPDATE ("
                        f"SELECT * FROM Treated_By WHERE "
                        f"out = '{current_user_id}' AND "
                        f"in = 'Patient:{patient_id}' "
                        f").in "
                        f"{set_string};"
                    )
                
                DatabaseErrorHelper(query_result, error_stack)
   
            except Exception as e:
                error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    UpdatePatientService
                ) 
            
            return ReturnAccessTokenHelper(current_user_id, error_stack)

        except Exception as e:
            ExceptionHelper(UpdatePatientService, error_stack, e)


'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval (even with empty array)
status.HTTP_403_FORBIDDEN  # when user doesn't have permission
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetAllPatientsByUserIDService(current_user_id, db, error_stack):
    try:
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
                    GetAllPatientsByUserIDService
                ) 
        
        result_without_status = query_result[0]['result']

        return ReturnAccessTokenHelper(current_user_id, error_stack), result_without_status
    
    except Exception as e:
        ExceptionHelper(GetAllPatientsByUserIDService, error_stack, e)
    

# Tested: Deleting the Patient automatically deletes the Treated_By relation too
'''insert check with output that shows the user if they can delete this patient'''
'''add Note deletion'''
'''
# Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion
status.HTTP_404_NOT_FOUND  # when patient doesn't exist
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to delete
status.HTTP_409_CONFLICT  # when patient can't be deleted (has dependencies)
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def DeletePatientService(patient_id, current_user_id, db, error_stack):
    try:
        # Delete Images
        try:
            json_response = await GetImagesByPatient(patient_id, current_user_id, db)
            images = json_response[1]
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "GetImagesByPatient error",
                    e,
                    DeletePatientService
                ) 
            
        try:
            for image in images:
                image_id = image['id']
                DeleteImageByID(image_id, current_user_id, db)
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DeleteImageByID error",
                    e,
                    DeletePatientService
                ) 

        # Delete Patients
        try:
            json_response = await GetAllReportsByPatientIDService(patient_id, current_user_id, db)
            reports = json_response[1]
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "GetAllReportsByPatientIDService error",
                    e,
                    DeletePatientService
                ) 

        try:
            for report in reports:
                report_id = report['id']
                DeleteReportService(report_id, current_user_id, db)
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DeleteReportService error",
                    e,
                    DeletePatientService
                ) 
 
        try: 
            query_result = await db.query(
                    f"DELETE "
                    f"(SELECT * FROM "
                    f"Treated_By WHERE "
                    f"in = {patient_id} and "
                    f"out = {current_user_id}).in;"
                )
            
            DatabaseErrorHelper(query_result, error_stack)
   
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Final Patient deletion Query error",
                    e,
                    DeletePatientService
                ) 
        
        if query_result[0] == '':
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Patient deletion successfull.",
                    "Null",
                    DeletePatientService
                )
                
    except Exception as e:
        ExceptionHelper(DeletePatientService, error_stack, e)



        