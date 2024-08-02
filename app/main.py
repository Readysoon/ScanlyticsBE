from fastapi import FastAPI
from fastapi.responses import HTMLResponse

import logging

from surreal.surrealdbController import router as surrealdb_router
from user.userController import router as user_router

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.include_router(surrealdb_router)
app.include_router(user_router)

# @app.on_event("startup")
# async def startup_event():
#     await init_db()
    # SurrealDB doesn't require explicit table creation; data entries create tables automatically.
    # You might want to insert initial data or perform checks here.

@app.get("/", response_class=HTMLResponse)
async def landing_page():
    html_content = """
    <html>
        <head>
            <title>Welcome</title>
        </head>
        <body>
            <h1>Welcome to the FastAPI App</h1>
            <p>To checkout the database itself, visit:</p>
            <a href="/surrealdb">Go to SurrealDB Operations</a>
            <p>To try creating the user table, visit:</p>
            <a href="user/create">Create the user table</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
