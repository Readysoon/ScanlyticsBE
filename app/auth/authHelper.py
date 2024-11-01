import datetime
from jose import jwt
import os
from surrealdb import Surreal

from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, status

from app.db.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# use the function only in try and except block
# print(data)
# = {'sub': 'User:jvoqozcbojb3yjmdcmzu'}
def CreateAccessTokenHelper(data: dict, error_stack):
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


# takes current_user_id only in the format without 'User:' ?! still needs to checked if actually true
def ReturnAccessTokenHelper(current_user_id, error_stack):
    try:
        # = {'sub': 'User:jvoqozcbojb3yjmdcmzu'}
        access_token = CreateAccessTokenHelper({"sub": current_user_id}, error_stack)
        
        return {"access_token": access_token, "token_type": "bearer"}
    except Exception as e:
        raise error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Creating the Access Token didnt work.", e, ReturnAccessTokenHelper.__name__)


def VerifyAccessTokenHelper(token):
    '''this doesnt make sense - or does it?'''
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
async def GetCurrentUserIDHelper(
    token:str = Depends(oauth2_scheme), 
    db: Surreal = Depends(get_db)
    ):
    
    # VerifyAccessTokenHelper returns the id when given the token
    try:
        user_id = VerifyAccessTokenHelper(token)
        print(f"GetCurrentUserIDHelper: {user_id}")
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
