import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi import FastAPI, Depends

import logging

# from db.seeds import seeddoc2patients
from app.db.models import initializedb

from app.db.surrealdbController import router as surrealdb_router
from app.user.userController import router as user_router
from app.patient.patientController import router as patient_router
from app.auth.authController import router as auth_router
from app.report.reportController import router as report_router
from app.image.imageController import router as image_router
from app.statement.statementController import router as statement_router
from app.note.noteController import router as note_router
from app.email.emailController import router as email_router
from app.classifier.classifierController import router as classifier_router
from app.ml_models.ml_modelsController import router as ml_models

from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded


logging.basicConfig(level=logging.INFO)


app = FastAPI()

# global slowapi rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["30/minute"])
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)


# handling validation exceptions more beautifull
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []
    
    for error in errors:
        error_location = " -> ".join(str(loc) for loc in error["loc"])
        error_messages.append({
            "location": error_location,
            "message": error["msg"],
            "type": error["type"]
        })

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation error",
            "detail": "One or more fields failed validation",
            "errors": error_messages
        }
    )


app.include_router(surrealdb_router)
app.include_router(user_router)
app.include_router(patient_router)
app.include_router(auth_router)
app.include_router(report_router)
app.include_router(image_router)
app.include_router(statement_router)
app.include_router(note_router)
app.include_router(email_router)
app.include_router(classifier_router)
app.include_router(ml_models)


'''to make InitializeStatementsService work it needs db as a parameter'''
@app.on_event("startup")
async def startup_event():
    await initializedb()
    # await InitializeStatementsService()
    

@app.get("/")
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

                    const return await fetch('auth/user_signup', {{
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
            <h1>Welcome to Scanlytics</h1>
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
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)

    
