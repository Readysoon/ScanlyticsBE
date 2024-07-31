from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from surrealdb import Surreal
from fastapi.responses import RedirectResponse
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI()

async def surreal_db_operations():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
    # use the following line to run uvicorn locally, the upper in docker
    # async with Surreal("ws://localhost:8000/rpc") as db:
    
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        create_response = await db.create(
            "person",
            {
                "user": "me",
                "pass": "safe",
                "marketing": True,
                "tags": ["python", "documentation"],
            },
        )
        logging.info(f"Create response: {create_response}")

        persons = await db.select("person")
        logging.info(f"Persons after creation: {persons}")

        update_response = await db.update("person", {
            "user": "you",
            "pass": "very_safe",
            "marketing": False,
            "tags": ["Awesome"]
        })
        # delete_response = await db.delete("person")

        query_response = await db.query("""
        insert into person {
            user: 'me',
            pass: 'very_safe',
            tags: ['python', 'documentation']
        };
        """)

        select_response = await db.query("select * from person")
        update_query_response = await db.query("""
        update person content {
            user: 'you',
            pass: 'more_safe',
            tags: ['awesome']
        };
        """)

        select_response = await db.query("select * from person")
        # delete_query_response = await db.query("delete person")

        return {
            "persons": persons,
            "update_response": update_response,
            # "delete_response": delete_response,
            "query_response": query_response,
            "select_response": select_response,
            "update_query_response": update_query_response,
            # "delete_query_response": delete_query_response,
            "select_response": select_response,
        }

@app.get("/surrealdbOP")
async def surrealdb_handler():
    result = await surreal_db_operations()
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
            <p>To perform operations with SurrealDB, visit the following link:</p>
            <a href="/surrealdbOP">Go to SurrealDB Operations</a>
            <p>To checkout the database itself, visit:</p>
            <a href="/surrealdb">Go to SurrealDB Operations</a>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
