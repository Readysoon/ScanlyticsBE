from fastapi import Depends, HTTPException, status
from surrealdb import Surreal
from passlib.context import CryptContext
from jose import jwt

from fastapi.security import OAuth2PasswordBearer

import os
import datetime

from scanlyticsbe.app.db.database import get_db

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


# retrieves the token from the HTTP request, extracts the user_id from it, 
# checks if it is in the database and returns the whole user
async def GetCurrentUserService(
    token:str = Depends(oauth2_scheme), 
    db: Surreal = Depends(get_db)
    ):
    
    # verify_access_token returns the id when given the token
    try:
        user_id = verify_access_token(token)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Verifying the access token didnt work: {e}")

    # from the id given by verify_access_token the user is selected in the database
    try: 
        query_result = await db.query(f"((SELECT * FROM User WHERE id = 'User:{user_id}').id)[0];")
        select_user_result = query_result[0]['result']
        if select_user_result == None:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Select User == None")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"Querying the user in get_current_user didnt work: {e}")
    
    return select_user_result


# only takes User IDs in the format "User:jhfdcoirrwueck"
def ReturnAccessTokenService(query_result):
    try:
        current_user_id = query_result[0]['result'][0]['id']

        access_token = create_access_token(data={"sub": current_user_id})

        print(access_token)

        return {"access_token": access_token, "token_type": "bearer"}

    except Exception as e:
        HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Access token creation didnt work: {e}")



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
    try: 
        try:
            create_orga_result = await db.query(
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
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database operation failed: {e}")   

        try: 
            print(f"BBBBBBBBBBBB: {create_orga_result}")
            print(f"AAAAAAAAAAAA: {ReturnAccessTokenService(create_orga_result)}")
            return ReturnAccessTokenService(create_orga_result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Access token returning failed: {e}")   

    except Exception as e:   
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user with orga didnt work: {e}")


'''A user can only join an organization if the owner acccepts'''  
# Organization:1 is for all doctors without an practice
async def UserSignupService(user_email, user_name, user_password, user_role, db):
    hashed_password = pwd_context.hash(user_password)
    try:
        try:
            create_user_result = await db.query(
                    f"CREATE User Set "
                    f"email = '{user_email}', "
                    f"name = '{user_name}', "
                    f"password = '{hashed_password}', "
                    f"role = '{user_role}', "
                    f"organization = Organization:1"
                )
            
        except Exception as e: 
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Database creation didnt work. {e}")
        
        try: 
            return ReturnAccessTokenService(create_user_result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Access token returning failed: {e}")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Adding the user without orga didnt work: {e}")
    

# this takes email and password and "logs in" meaning it checks in the database 
# if the two match and then returns the access token valid for 15 min
async def LoginService(db, user_data):
    try:
        try:
            login_query_result = await db.query(
                    f"SELECT id, email, password "
                    f"FROM User WHERE "
                    f"email = '{user_data.username}';"
                )
            
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Querying didnt work: {e}")
        if not login_query_result[0]['result']:
            # user not found
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Wrong credentials")
        
        if not pwd_context.verify(user_data.password, login_query_result[0]['result'][0]['password']):
            # wrong password
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="wrong credentials")
        
        try: 
            return ReturnAccessTokenService(login_query_result)
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Access token returning failed: {e}")

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Login didnt work: {e}")





    