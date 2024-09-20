from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from scanlyticsbe.app.db.database import get_db

from surrealdb import Surreal
from fastapi import Depends
from scanlyticsbe.app.db.database import get_db

import logging
from dotenv import load_dotenv
import os

'''For Gcloud deploying add "." to the imports and remove for development.'''

# from db.seeds import seeddoc2patients
from scanlyticsbe.app.db.models import initializedb
from scanlyticsbe.app.db.surrealdbController import router as surrealdb_router
from scanlyticsbe.app.user.userController import router as user_router
from scanlyticsbe.app.patient.patientController import router as patient_router
from scanlyticsbe.app.auth.authController import router as auth_router


logging.basicConfig(level=logging.INFO)

app = FastAPI()


app.include_router(surrealdb_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(auth_router)

'''to implement: seed()'''
@app.on_event("startup")
async def startup_event():
    await initializedb()

@app.get("/", response_class=HTMLResponse)
async def landing_page(
    db: Surreal = Depends(get_db)
    ):
    query_result = await db.query(f"INFO FOR DB;")
    html_content = f"""
    <html>
        <head>
            <title>Welcome</title>
        </head>
        <body>
            <h1>Welcome test to Scanlytics</h1>
            <p>To checkout the database itself, visit:</p>
            <a href="/surrealdb">SurrealDB</a>
            <p>To create the seed user, visit:</p>
            <a href="/seed/orga_user">Seed the user</a>
            <p>{query_result}</p>
        </body>
    </html>
    """
    # print(query_result)
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
