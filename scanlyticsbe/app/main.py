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
from scanlyticsbe.app.report.reportController import router as report_router
from scanlyticsbe.app.image.imageController import router as image_router


logging.basicConfig(level=logging.INFO)

app = FastAPI()


app.include_router(surrealdb_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(auth_router)
app.include_router(report_router)
app.include_router(image_router)


'''to implement: seed()'''
@app.on_event("startup")
async def startup_event():
    await initializedb()

@app.get("/", response_class=HTMLResponse)
async def landing_page(
    ):
    html_content = f"""
    <html>
        <head>
            <title>Welcome</title>
            <script>
                async function signup(event) {{
                    event.preventDefault(); // Prevent form submission

                    const formData = new FormData(event.target);
                    const data = {{
                        user_email: formData.get('user_email'),
                        user_name: formData.get('user_name'),
                        user_password: formData.get('user_password'),
                        user_role: formData.get('user_role')
                    }};

                    const response = await fetch('auth/user_signup', {{
                        method: 'POST',
                        headers: {{
                            'Content-Type': 'application/json',
                        }},
                        body: JSON.stringify(data),
                    }});

                    const result = await response.json();
                    alert(result.message || 'Signup succesful or unsuccessful :)');
                }}
            </script>
        </head>
        <body>
            <h1>Welcome test to Scanlytics</h1>
            <p>To checkout the database itself, visit:</p>
            <a href="/surrealdb">SurrealDB</a>
            <h2>Signup</h2>
            <form onsubmit="signup(event)">
                <label for="user_email">Email:</label><br>
                <input type="email" id="user_email" name="user_email" required><br>
                <label for="user_name">Name:</label><br>
                <input type="text" id="user_name" name="user_name" required><br>
                <label for="user_password">Password:</label><br>
                <input type="password" id="user_password" name="user_password" required><br>
                <label for="user_role">Role:</label><br>
                <input type="text" id="user_role" name="user_role" required><br><br>
                <input type="submit" value="Signup">
            </form>
        </body>
    </html>
    """

    # print(query_result)
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
