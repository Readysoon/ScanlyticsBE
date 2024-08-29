from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import logging
from dotenv import load_dotenv
import os

'''For Gcloud deploying add "." to the imports and remove for development.'''

# from db.seeds import seeddoc2patients
from app.db.models import initializedb
from app.db.surrealdbController import router as surrealdb_router
from app.user.userController import router as user_router
from app.patient.patientController import router as patient_router
from app.auth.authController import router as auth_router


logging.basicConfig(level=logging.INFO)

'''load_dotenv and the '''
# Load the .env file
load_dotenv()

SURREALDB_URL = os.getenv('SURREALDB_URL')
SURREALDB_USER = os.getenv('SURREALDB_USER')
SURREALDB_PASS = os.getenv('SURREALDB_PASS')
SURREALDB_NAMESPACE = os.getenv('SURREALDB_NAMESPACE')
SURREALDB_DATABASE = os.getenv('SURREALDB_DATABASE')
SECRET_KEY = os.getenv('secret_key')

app = FastAPI()

app.include_router(surrealdb_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(auth_router)

'''to implement: seed()'''
@app.on_event("startup")
async def startup_event():
    await initializedb()
    # await seed()

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    html_content = """
    <html>
        <head>
            <title>Welcome</title>
        </head>
        <body>
            <h1>Welcome to the Scanlytics App</h1>
            <p>To checkout the database itself, visit:</p>
            <a href="/surrealdb">SurrealDB</a>
            <p>To create the Praxis (Diagnostikum), visit:</p>
            <a href="/praxis/create">Create Praxis:Diagnostikum</a>
            <p>To try creating the user table, visit:</p>
            <a href="user/create">Create the user table</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
