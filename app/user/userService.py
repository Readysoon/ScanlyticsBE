from surrealdb import Surreal
from pydantic import BaseModel
from fastapi import HTTPException, status
from passlib.context import CryptContext
from starlette.responses import JSONResponse

from app.auth.authService import DatabaseResultService, ReturnAccessTokenHelper
from app.patient.patientService import DeletePatientService, GetAllPatientsByUserID

from app.error.errorService import ErrorStack

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  



'''	1.	Get user profile
	2.	Update user profile
	3.	Delete user account
	4.	Change password (when already logged in)
	5.	Get user preferences
	6.	Update user preferences
	7.	User search/listing (for admin purposes)
'''


async def GetCurrentUserService(current_user_id, db):
    try:
        try: 
            query_result = await db.query(
                f"SELECT * FROM "
                f"User WHERE "
                f"id = '{current_user_id}'"
            )
            
            DatabaseResultService(query_result)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        return ReturnAccessTokenHelper(current_user_id), query_result[0]['result'][0]

    except:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"GetCurrentUserService: {e}")   
    

async def PatchUserService(userin, current_user_id, db):
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
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Set-string creation failed: {e}")   
        
        try: 
            # and finally put everything together and send it
            query_result = await db.query(
                    f"UPDATE "
                    f"{current_user_id} "
                    f"{set_string};"
                )
            
            DatabaseResultService(query_result)

        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work: {e}")
        
        return ReturnAccessTokenHelper(current_user_id)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Updating the user didnt work: {e}")
    

async def DeleteUserService(current_user_id, db):
    error_stack = ErrorStack()

    try:
        query_result = await db.query(
            f"SELECT * FROM User "
            f"WHERE id = {current_user_id};"
        )

        db_exception_handler = DatabaseResultService(query_result)
        if db_exception_handler.errors:
            for error in db_exception_handler.errors:
                error_stack.add_error(error["code"], error["detail"], error.get("function"))

    except Exception as e:
        error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Query error.", DeleteUserService.__name__)

    if not query_result[0]['result']:
        raise error_stack.add_error(status.HTTP_404_NOT_FOUND, "No such user.", DeleteUserService.__name__)

    try:             
        try:
            json_response = await GetAllPatientsByUserID(current_user_id, db)
            patients = json_response[1]
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"GetAllPatientsByUserID: {e}")
        
        try:
            for patient in patients:
                patient_id = patient['in']
                DeletePatientService(patient_id, db, current_user_id)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Patient deletion error: {e}")
        
        try:
            query_result = await db.query(
                f"DELETE {current_user_id};"
            )
            DatabaseResultService(query_result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"User deletion error: {e}")
        
        try:
            query_result = await db.query(
                f"SELECT * FROM User "
                f"WHERE id = {current_user_id};"
            )

            db_exception_handler = DatabaseResultService(query_result)
            if db_exception_handler.errors:
                for error in db_exception_handler.errors:
                    error_stack.add_error(error["code"], error["detail"], error.get("function"))

        except Exception as e:
            error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Query error.", DeleteUserService.__name__)

        if not query_result[0]['result']:
            return JSONResponse(status_code=200, content={"message": "User deletion successful."})
        else: 
            return JSONResponse(status_code=500, content={"message": "User deletion unsuccessful."})
        
    except Exception as e:
        print(f"{DeleteUserService.__name__}: Printed error stack: \n{error_stack}")
        last_error = error_stack.get_last_error()
        if last_error:
            raise HTTPException(status_code=last_error["code"], detail=f"Function: {last_error.get('function', 'Unknown')}, Detail: {last_error['detail']}")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))