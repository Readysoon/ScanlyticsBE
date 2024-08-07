from fastapi import Depends, HTTPException, status
from surrealdb import Surreal

from passlib.context import CryptContext


from db.database import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def signup_service(username, password, db: Surreal = Depends(get_db)):
    # Select a specific record from a table
    # In the secure surrealDB way: 
    results = await db.query("SELECT * FROM user WHERE mail = $username", {"username": username})
    # check if there are results:
    if results and 'result' in results[0] and len(results[0]['result']) > 0:
        # Extract the mail from the first record in the result set
        user_mail_in_db = results[0]['result'][0]['mail']
        if username == user_mail_in_db:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
    else: 
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Email not registered"
        )
    
    

        


