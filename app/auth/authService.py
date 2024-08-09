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
        # [
        #   {
        #       'result': [
        #           {
        #               'id': 'user:ctpgpv30btvkjxkvhd9q',
        #               'mail': 'haha@gmail.com', 
        #               'password': '1234',
        #               'praxis': 'praxis:diagnostikum'
        #            }
        #        ],
        #       'status': 'OK',
        #       'time': '481.125µs'
        #   }
        # ]
        user_mail_in_db = results[0]['result'][0]['mail']
        # if it doesnt match then theres no user with this mail in the database
        if not username == user_mail_in_db:
            hashed_password =  pwd_context.hash(password)
            print(username)
            print(hashed_password)
            raise HTTPException(
                status_code=status.HTTP_201_CREATED, detail="Email not registered")
    # if theres no result for this username/mail return the exception:
        else: 
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
            )
            


