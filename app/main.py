from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import os

import redis.asyncio as redis
from fastapi_limiter import FastAPILimiter

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

from app.error.errorHelper import RateLimit



from fastapi import FastAPI, Request, status
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError



logging.basicConfig(level=logging.INFO)

app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    error_messages = []

    print(errors)
    
    for error in errors:
        error_location = " -> ".join(str(loc) for loc in error["loc"])
        error_messages.append({
            "location": error_location,
            "message": error["msg"],
            "type": error["type"]
        })
        
        # Special handling for email validation errors
        if "email" in error_location.lower() and error["type"] == "value_error":
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "message": "Invalid email format",
                    "detail": "Please provide a valid email address",
                    "errors": error_messages
                }
            )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Validation error",
            "detail": "One or more fields failed validation",
            "errors": error_messages
        }
    )

@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Data validation error",
            "detail": exc.errors(),
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
    redis_url = os.getenv("REDIS_URL")
    redis_connection = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    # await InitializeStatementsService()
    

@app.get("/")# , dependencies=[Depends(RateLimiter(times=2, seconds=5))])
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
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

    
