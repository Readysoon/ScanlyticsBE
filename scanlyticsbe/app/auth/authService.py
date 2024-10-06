from fastapi import Depends, HTTPException, status
from surrealdb import Surreal
from passlib.context import CryptContext
from jose import jwt

from fastapi.security import OAuth2PasswordBearer

import os
import datetime

from scanlyticsbe.app.db.database import get_db, DatabaseResultService

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")  


# print(data)
# = {'sub': 'User:jvoqozcbojb3yjmdcmzu'}
#
# == Write this if you want to return the token to the user == 
# access_token = create_access_token(data={"sub": user_id})
# and return it as the final answer to the user
# return {"access_token": access_token, "token_type": "bearer"}
def create_access_token(data: dict):
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


def verify_access_token(token):
    try:
        SECRET_KEY = os.getenv("secret_key")
        if SECRET_KEY == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Secret Key is None.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Secret key couldnt be obtained: {e}")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Decoding the payload didnt work: {e}")
    id: str = payload.get("sub")
    return id


# returns format User:hus842hjs98ou2i
async def GetCurrentUserIDService(
    token:str = Depends(oauth2_scheme), 
    db: Surreal = Depends(get_db)
    ):
    
    # verify_access_token returns the id when given the token
    try:
        user_id = verify_access_token(token)
        print(f"GetCurrentUserIDService: {user_id}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Verifying the access token didnt work: {e}")

    # from the id given by verify_access_token the user is selected in the database
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


def ReturnAccessTokenService(current_user_id):
    try:
        access_token = create_access_token(data={"sub": current_user_id})
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"ReturnAccessTokenService: {e}")


# before creating an account the mail should be checked so the user doesnt fill out the whole signup form just to be rejected
async def CheckMailService(user_email, db):
    try:
        result = await db.query(
                f"SELECT VALUE email FROM User WHERE "
                f"email = '{user_email}';"
            )
        
        email = result[0]['result']
        
        if email:
            return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Email in use")
        else:
            return HTTPException(status_code=status.HTTP_202_ACCEPTED, detail="Email can be registered")         
         
    except: 
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Something querying the email didnt work")


# an user can only exist within an organization -> the first creates it, the others join
'''logic for joining an organization has to be yet implemented'''
async def OrgaSignupService(user_email, user_name, user_password, user_role, orga_address, orga_email, orga_name, db):
    hashed_password = pwd_context.hash(user_password)
    print(user_email)
    try: 
        try:
            query_result = await db.query(
                    f"CREATE User Set "
                    f"email = '{user_email}', "
                    f"name = '{user_name}', "
                    f"password = '{hashed_password}', "
                    f"role = '{user_role}', "
                    f"organization = "
                    f"((CREATE Organization Set "
                    f"address = '{orga_address}', "
                    f"name = '{orga_name}', "
                    f"email = '{orga_email}'"
                    f").id)[0]"
                )
            
            DatabaseResultService(query_result)
   
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation failed: {e}")  

        return ReturnAccessTokenService(query_result[0]['result'][0]['id'])

    except Exception as e:   
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user with orga didnt work: {e}")


'''A user can only join an organization if the owner acccepts'''  
# Organization:1 is for all doctors without an practice
async def UserSignupService(user_email, user_name, user_password, user_role, db):
    hashed_password = pwd_context.hash(user_password)
    try:
        try:
            query_result = await db.query(
                    f"CREATE User Set "
                    f"email = '{user_email}', "
                    f"name = '{user_name}', "
                    f"password = '{hashed_password}', "
                    f"role = '{user_role}', "
                    f"organization = Organization:1"
                )
            
            DatabaseResultService(query_result)
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation didnt work. {e}")
        
        return ReturnAccessTokenService(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user without orga didnt work: {e}")
    

# this takes email and password and "logs in" meaning it checks in the database 
# if the two match and then returns the access token valid for 15 min
async def LoginService(db, user_data):
    try:
        try:
            query_result = await db.query(
                    f"SELECT id, email, password "
                    f"FROM User WHERE "
                    f"email = '{user_data.user_email}';"
                )
            
            DatabaseResultService(query_result)
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying didnt work: {e}")
        
        if not query_result[0]['result']:
            # user not found
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Wrong credentials")
        
        if not pwd_context.verify(user_data.user_password, query_result[0]['result'][0]['password']):
            # wrong password
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong credentials")
        
        return ReturnAccessTokenService(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")
    
async def update_password_service(password, current_user_id, db):
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
        return ReturnAccessTokenService(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")
    
async def ValidateService(current_user_id, db):
    try:
        try:
            query_result = await db.query(
                    f"SELECT id "
                    f"FROM User WHERE "
                    f"id = '{current_user_id}';"
                )
            
            DatabaseResultService(query_result)
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying didnt work: {e}")
        
        print(query_result)
        return ReturnAccessTokenService(query_result[0]['result'][0]['id'])

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")
