from fastapi import Depends, HTTPException, status
from surrealdb import Surreal
from passlib.context import CryptContext
from jose import jwt

from fastapi.security import OAuth2PasswordBearer
from starlette.responses import JSONResponse

import os
import datetime

from app.db.database import get_db, DatabaseResultService
from app.email.emailService import EmailVerificationService
from app.error.errorService import ErrorStack

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  


# print(data)
# = {'sub': 'User:jvoqozcbojb3yjmdcmzu'}
def CreateAccessTokenHelper(data: dict):
    to_encode = data.copy()
    try:
        SECRET_KEY = os.getenv("secret_key")
        if SECRET_KEY == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Secret Key is None.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Secret key couldnt be obtained: {e}")
    
    expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)

    # surreal creates an ID wrapped in ankle brackets which the following line extracts
    try:
        to_encode['sub'] = to_encode['sub'].split(":")[1].strip("⟨⟩")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ID extraction didnt work: {e}")
    
    try:
        to_encode.update({"exp": expire})
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Updating to_encode didnt work: {e}")
    
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

        return encoded_jwt
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Encoding and returning the jwt-token didnt work: {e}")


def VerifyAccessTokenHelper(token):
    '''this doesnt make sense'''
    try:
        SECRET_KEY = os.getenv("secret_key")
        if SECRET_KEY == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Secret Key is None.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Secret key couldnt be obtained: {e}")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"VerifyAccessTokenHelper: {e}")
    id: str = payload.get("sub")
    return id


# returns format User:hus842hjs98ou2i
async def GetCurrentUserIDService(
    token:str = Depends(oauth2_scheme), 
    db: Surreal = Depends(get_db)
    ):
    
    # VerifyAccessTokenHelper returns the id when given the token
    try:
        user_id = VerifyAccessTokenHelper(token)
        print(f"GetCurrentUserIDService: {user_id}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Verifying the access token didnt work: {e}")

    # from the id given by VerifyAccessTokenHelper the user is selected in the database
    # can also be: (SELECT id FROM User WHERE id = 'User:bsb2xdhxgn0arxgjp8mq')[0].id
    try: 
        query_result = await db.query(f"((SELECT * FROM User WHERE id = 'User:{user_id}').id)[0];")
        select_user_result = query_result[0]['result']
        if select_user_result == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Select User == None")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Querying the user in GetCurrentUserService didnt work: {e}")
    
    return select_user_result

# takes current_user_id only in the format without 'User:' ?! still needs to checked if actually true
def ReturnAccessTokenHelper(current_user_id):
    try:
        access_token = CreateAccessTokenHelper(data={"sub": current_user_id})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ReturnAccessTokenHelper: {e}")


'''potential security risk'''
# before creating an account the mail should be checked so the user doesnt fill out the whole signup form just to be rejected
async def CheckMailService(user_email, db):
    error_stack = ErrorStack()

    try:
        query_result = await db.query(
                f"SELECT VALUE email FROM User WHERE "
                f"email = '{user_email}';"
            )
        
        db_exception_handler = DatabaseResultService(query_result)
        if db_exception_handler.errors:
            for error in db_exception_handler.errors:
                error_stack.add_error(error["code"], error["detail"], error.get("function"))
        
        email = query_result[0]['result']
        
        if email:
            return JSONResponse(status_code=226, content={"message": "Email in use."})    
        else:
            return JSONResponse(status_code=200, content={"message": "Email can be used."})    
                     
    except Exception as e:
        print(f"{CheckMailService.__name__}: Printed error stack: \n{error_stack}")
        last_error = error_stack.get_last_error()
        if last_error:
            raise HTTPException(status_code=last_error["code"], detail=f"Function: {last_error.get('function', 'Unknown')}, Detail: {last_error['detail']}")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))


# an user can only exist within an organization -> the first creates it, the others join
'''logic for joining an organization has to be yet implemented'''
async def OrgaSignupService(user_in, db):
    hashed_password = pwd_context.hash(user_in.user_password)
    try: 
        try:
            query_result = await db.query(
                    f"CREATE User Set "
                    f"email = '{user_in.user_email}', "
                    f"name = '{user_in.user_name}', "
                    f"password = '{hashed_password}', "
                    f"role = '{user_in.user_role}', "
                    f"organization = "
                    f"((CREATE Organization Set "
                    f"address = '{user_in.orga_address}', "
                    f"name = '{user_in.orga_name}', "
                    f"email = '{user_in.orga_email}'"
                    f").id)[0]"
                )
            
            DatabaseResultService(query_result)
   
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation failed: {e}")  

        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:   
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user with orga didnt work: {e}")


'''A user can only join an organization if the owner acccepts'''  
# Organization:1 is for all doctors without an practice
async def UserSignupService(user_in, db):
    hashed_password = pwd_context.hash(user_in.user_password)
    try:
        try:
            query_result = await db.query(
                    f"CREATE User Set "
                    f"email = '{user_in.user_email}', "
                    f"name = '{user_in.user_name}', "
                    f"password = '{hashed_password}', "
                    f"role = '{user_in.user_role}', "
                    f"organization = Organization:1"
                )
            
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
    
        token = ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])['access_token']
    
        try:
            first_name = user_in.user_name.split()[0]
            
            '''proper solution for testing has to be found'''
            await EmailVerificationService(user_in.user_email, token, first_name)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Sending the verification mail didnt work: {e}")
        
        '''proper solution for testing has to be found'''
        return JSONResponse(status_code=201, content={"message": f"Verification mail has been sent to {user_in.user_email}."})
        # return JSONResponse(status_code=201, content=ReturnAccessTokenHelper(query_result[0]['result'][0]['id']))
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user without orga didnt work: {e}")
    

async def LoginService(user_data, db):
    error_stack = ErrorStack()

    try:
        try:
            query_result = await db.query(
                f"SELECT id, email, password, verified "
                f"FROM User WHERE "
                f"email = '{user_data.user_email}';"
            )

            db_exception_handler = DatabaseResultService(query_result)
            if db_exception_handler.errors:
                for error in db_exception_handler.errors:
                    error_stack.add_error(error["code"], error["detail"], error.get("function"))

        except Exception as e:
            error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, "Query error.", LoginService.__name__)

        if not query_result or not query_result[0]['result']:
            error_stack.add_error(status.HTTP_404_NOT_FOUND, "User not found.", LoginService.__name__)
        else:
            if not query_result[0]['result'][0]['verified']:
                error_stack.add_error(status.HTTP_401_UNAUTHORIZED, "You have not verified your email.", LoginService.__name__)

            if not pwd_context.verify(user_data.user_password, query_result[0]['result'][0]['password']):
                error_stack.add_error(status.HTTP_401_UNAUTHORIZED, "Wrong password.", LoginService.__name__)

        if error_stack.errors:
            raise error_stack

        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:
        print(f"{LoginService.__name__}: Printed error stack: \n{error_stack}")
        last_error = error_stack.get_last_error()
        if last_error:
            raise HTTPException(status_code=last_error["code"], detail=f"Function: {last_error.get('function', 'Unknown')}, Detail: {last_error['detail']}")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

    
async def UpdatePasswordService(password, current_user_id, db):
    hashed_password = pwd_context.hash(password.password)
    try:
        try:
            query_result = await db.query(
                    f"UPDATE ("
                    f"SELECT id "
                    f"FROM User WHERE "
                    f"id = '{current_user_id}') "
                    f"SET password = '{hashed_password}';"
                )
            
            DatabaseResultService(query_result)
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying didnt work: {e}")
        
        print(query_result)
        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")
    

async def ValidateService(current_user_id, db):
    try:
        try:
            query_result = await db.query(
                    f"SELECT id "
                    f"FROM User WHERE "
                    f"id = '{current_user_id}' AND "
                    f"verified = true;"
                )
            
            DatabaseResultService(query_result)
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying didnt work: {e}")
        
        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")
    

async def VerificationService(token, db):
    error_stack = ErrorStack()
    
    try:
        current_user_id = VerifyAccessTokenHelper(token)

        try:
            query_result = await db.query(
                    f"Update ("
                    f"SELECT * "
                    f"FROM User WHERE "
                    f"id = 'User:{current_user_id}'"
                    f") SET "
                    f"verified = true;"
                )
            
            db_exception_handler = DatabaseResultService(query_result)
            if db_exception_handler.errors:
                for error in db_exception_handler.errors:
                    error_stack.add_error(error["code"], error["detail"], error.get("function"))
            
        except Exception as e:
            error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Query error: {e}", VerificationService.__name__)
        
        return ReturnAccessTokenHelper(query_result[0]['result'][0]['id']), {"message": f"{query_result[0]['result'][0]['email']} has been verified"}

    except Exception as e:
        print(f"{LoginService.__name__}: Printed error stack: \n{error_stack}")
        last_error = error_stack.get_last_error()
        if last_error:
            raise HTTPException(status_code=last_error["code"], detail=f"Function: {last_error.get('function', 'Unknown')}, Detail: {last_error['detail']}")
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

