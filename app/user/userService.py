from surrealdb import Surreal
from pydantic import BaseModel

import logging

# Define the User schema
class User(BaseModel):
    mail: str
    password: str
    praxis: str

async def CreateUserService():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        praxis_object = await db.query(f"SELECT id FROM praxis WHERE name = 'diagnostikum';")

        print("trying out user Service")
        print(praxis_object)

        praxis_id = praxis_object[0]["result"][0]["id"]

        print(praxis_id)

        create_response = await db.query(
                f"CREATE user SET mail = 'haha@gmail.com', password = '1234', praxis = {praxis_id};"
            )
        
        logging.info(f"Create response: {create_response}")