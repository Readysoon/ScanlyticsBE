from surrealdb import Surreal

async def get_db():
    db = Surreal()
    await db.connect("http://localhost:8000/rpc")  # replace with your SurrealDB endpoint
    await db.signin({"user": "root", "pass": "root"})  # replace with your SurrealDB credentials
    await db.use("test", "test")  # replace with your database and namespace
    try:
        yield db
    finally:
        await db.close()
