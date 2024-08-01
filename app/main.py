from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from surrealdb import Surreal
from fastapi.responses import RedirectResponse
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()
    
async def CreateUserService():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        create_response = await db.query(
            "DEFINE TABLE user schemafull;"
            "DEFINE FIELD mail on user type string;"
        )
        
        logging.info(f"Create response: {create_response}")
    
@app.get("/create_user")
async def create_user():
    result = await CreateUserService()
    return result

@app.get("/surrealdb")
async def surrealdb_handler():
    # Instead of returning the result, redirect to the desired URL
    return RedirectResponse(url="http://0.0.0.0:8000")

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
            <a href="/create_user">Create the user table</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
