from fastapi import status
from passlib.context import CryptContext
from starlette.responses import JSONResponse

from app.auth.authService import ReturnAccessTokenHelper
from app.patient.patientService import DeletePatientService, GetAllPatientsByUserIDService

from app.error.errorHelper import ExceptionHelper, DatabaseErrorHelper 


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  


'''	1.	Get user profile
	2.	Update user profile
	3.	Delete user account
	4.	Change password (when already logged in)
	5.	Get user preferences
	6.	Update user preferences
	7.	User search/listing (for admin purposes)
'''


# make this proper; you cant just claim a not found when theres a main exception
'''
# Suggested:
status.HTTP_200_OK  # for successful retrieval
status.HTTP_404_NOT_FOUND  # when user not found
status.HTTP_401_UNAUTHORIZED  # when token is invalid
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def GetCurrentUserService(current_user_id, db, error_stack):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM "
                f"User WHERE "
                f"id = '{current_user_id}'"
            )
            
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    GetCurrentUserService
                )
        
        return ReturnAccessTokenHelper(current_user_id, error_stack), query_result[0]['result'][0]

    except Exception  as e:
        ExceptionHelper(GetCurrentUserService, error_stack, e)
    
'''
# Suggested:
status.HTTP_200_OK  # for successful update
status.HTTP_400_BAD_REQUEST  # for invalid input data
status.HTTP_409_CONFLICT  # for email already in use
status.HTTP_422_UNPROCESSABLE_ENTITY  # for validation errors
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
'''patching mail should send new verification and set account to unverified'''
async def PatchUserService(userin, current_user_id, db, error_stack):
    try:
        try:
            email = userin.user_email
            name = userin.user_name
            password = userin.user_password
            role = userin.user_role
            set_string = "SET "

            # elongate the update_string
            if email:
                set_string += f"email = '{email}', "
            if name:
                set_string += f"name = '{name}', "
            if password:
                set_string += f"date_of_birth = '{password}', "
            if role:
                set_string += f"gender = '{role}', "

            set_string = set_string[:-2]

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Set-string creation failed.",
                    e,
                    PatchUserService
                )
                    
        try: 
            # and finally put everything together and send it
            query_result = await db.query(
                    f"UPDATE "
                    f"{current_user_id} "
                    f"{set_string};"
                )
            
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                    status.HTTP_500_INTERNAL_SERVER_ERROR,
                    "Query error.",
                    e,
                    PatchUserService
                )
        try:   

            return JSONResponse(
                status_code=200, 
                content=ReturnAccessTokenHelper(query_result[0]['result'][0]['id'], error_stack)
                )
        
        except Exception as e:
            if query_result is None:
                pass
            elif "already contains" in query_result[0]['result']:
                error_stack.add_error(
                    status.HTTP_409_CONFLICT,
                    f"Email '{userin.user_email}' is already registered.", 
                    e,
                    PatchUserService
                )
            else:
                error_stack.add_error(
                        status.HTTP_500_INTERNAL_SERVER_ERROR,
                        "JSON Response error.",
                        e,
                        PatchUserService
                    )

    except Exception as e:
        ExceptionHelper(PatchUserService, error_stack, e)
    
'''
# Suggested:
status.HTTP_204_NO_CONTENT  # for successful deletion
status.HTTP_404_NOT_FOUND  # when user not found
status.HTTP_409_CONFLICT  # when deletion fails due to dependencies
status.HTTP_500_INTERNAL_SERVER_ERROR  # keep for actual server errors
'''
async def DeleteUserService(current_user_id, db, error_stack):
    try:
        query_result = await db.query(
            f"SELECT * FROM User "
            f"WHERE id = {current_user_id};"
        )

        DatabaseErrorHelper(query_result, error_stack)

    except Exception as e:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Search User Query error.",
                e,
                DeleteUserService
            )

    if not query_result[0]['result']:
        error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "No such user.",
                "None",
                DeleteUserService
            )

    try:             
        try:
            json_response = await GetAllPatientsByUserIDService(current_user_id, db, error_stack)
            patients = json_response[1]
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "GetAllPatientsByUserIDService.",
                e,
                DeleteUserService
            )
        
        try:
            for patient in patients:
                patient_id = patient['in']
                DeletePatientService(patient_id, db, current_user_id)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "DeletePatientService.",
                e,
                DeleteUserService
            )
        
        try:
            query_result = await db.query(
                f"DELETE {current_user_id};"
            )
            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Delete query error.",
                e,
                DeleteUserService
            )

        try:
            query_result = await db.query(
                f"SELECT * FROM User "
                f"WHERE id = {current_user_id};"
            )

            DatabaseErrorHelper(query_result, error_stack)

        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Controll query error.",
                e,
                DeleteUserService
            )
        
        try:
            if not query_result[0]['result']:
                return JSONResponse(status_code=200, content={"message": "User deletion successful."})
            else: 
                return JSONResponse(status_code=500, content={"message": "User deletion unsuccessful."})
            
        except Exception as e:
            error_stack.add_error(
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                "Returning JSONResponse failed.",
                e,
                DeleteUserService
            )
        
    except Exception as e:
        ExceptionHelper(DeleteUserService, error_stack, e)