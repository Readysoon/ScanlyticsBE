from fastapi import status
from starlette.responses import JSONResponse


from app.auth.authService import ReturnAccessTokenHelper

from app.report.reportService import DeleteReportService
from app.report.reportHelper import GetAllReportsByPatientIDHelper

from app.image.imageHelper import GetImagesByPatientHelper, DeleteImageByIDHelper
from app.patient.patientHelper import GetAllPatientsByUserIDHelper, GetPatientByIDHelper
from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 

'''
# Suggested:
status.HTTP_201_CREATED  # for successful creation - check
status.HTTP_400_BAD_REQUEST  # for invalid patient data - to be done in schema check
status.HTTP_409_CONFLICT  # if patient already exists - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def CreatePatientService(patientin, current_user_id, db, error_stack):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM Patient "
                f"WHERE name = '{patientin.patient_name}';"
            )

        except Exception as e: 
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    CreatePatientService
                ) 
            
        if query_result[0]['result']:
            error_stack.add_error(
                    status.HTTP_409_CONFLICT,
                    f"A patient with the name '{patientin.patient_name}' already exists.",
                    "None",
                    CreatePatientService
                ) 
            
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
        
        result_without_status = query_result[0]['result'][0]

        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Created patient."
                    }, 
                    result_without_status,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
            
    except Exception as e:
        ExceptionHelper(CreatePatientService, e, error_stack)


# Looks with the patient_id and current_user_id which patients are to user 
# with the id and returns information about the patient
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval -check
status.HTTP_404_NOT_FOUND  # when patient doesn't exist (change from 500) - check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to access patient - check
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors -check 
'''
async def GetPatientByIDService(patient_id, current_user_id, db, error_stack):
    try:
        patient = await GetPatientByIDHelper(patient_id, current_user_id, db, error_stack)

        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Fetched patient data."
                    }, 
                    patient,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
    
    except Exception as e:
        ExceptionHelper(GetPatientByIDService, e, error_stack)

'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval (even with empty array) -check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission - redundant
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors - check
'''
async def GetAllPatientsByUserIDService(current_user_id, db, error_stack):

    try:
        patient_list = await GetAllPatientsByUserIDHelper(current_user_id, db, error_stack)

        patient_count = 0

        for patient in patient_list:
            patient_count += 1


        return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Fetched all {patient_count} patient(s) for user '{current_user_id}'."
                    }, 
                    patient_list,
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
    
    except Exception as e:
        ExceptionHelper(GetAllPatientsByUserIDService, e, error_stack)


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
            patient = await GetPatientByIDHelper(patient_id, current_user_id, db, error_stack)

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
            
            return JSONResponse(
                status_code=200, 
                content=[
                    {
                        "message": f"Updated patient."
                    }, 
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )

        except Exception as e:
            ExceptionHelper(UpdatePatientService, e, error_stack)

    

# Tested: Deleting the Patient automatically deletes the Treated_By relation too
'''insert check with output that shows the user if they can delete this patient'''
'''add Note deletion'''
'''
# Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion
status.HTTP_404_NOT_FOUND  # when patient doesn't exist -check
status.HTTP_403_FORBIDDEN  # when user doesn't have permission to delete -check
status.HTTP_409_CONFLICT  # when patient can't be deleted (has dependencies) - doesnt make sense
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def DeletePatientService(patient_id, current_user_id, db, error_stack):

    patient = await GetPatientByIDHelper(patient_id, current_user_id, db, error_stack)

    try:
        # Delete Images
        try:
            image_list = await GetImagesByPatientHelper(patient_id, current_user_id, db, error_stack)
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "GetImagesByPatientHelper error",
                    e,
                    DeletePatientService
                ) 
            
        try:
            for image in image_list:
                image_id = image['id']
                DeleteImageByIDHelper(image_id, current_user_id, db, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "DeleteImageByIDHelper error",
                    e,
                    DeletePatientService
                ) 

        # Delete Reports
        try:
            report_list = await GetAllReportsByPatientIDHelper(patient_id, current_user_id, db, error_stack)
        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "GetAllReportsByPatientIDService error",
                    e,
                    DeletePatientService
                ) 

        try:
            for report in report_list:
                report_id = report['id']
                DeleteReportService(report_id, current_user_id, db, error_stack)
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
        
        if not query_result[0]['result'] and query_result[0]['status'] == 'OK':
            return JSONResponse(
                status_code=204, 
                content=[
                    {
                        "message": f"Deleted patient '{patient_id}'."
                    }, 
                    ReturnAccessTokenHelper(current_user_id, error_stack)
                    ]
                )
                
    except Exception as e:
        ExceptionHelper(DeletePatientService, e, error_stack)



        