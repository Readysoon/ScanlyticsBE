from surrealdb import Surreal

import logging

async def CreateUserService():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        create_response = await db.query(
            "DEFINE TABLE praxis schemafull;"
            
            "DEFINE TABLE user schemafull;"
            "DEFINE FIELD mail on user type string;"
            "DEFINE FIELD password on user type string;"
            "DEFINE FIELD praxis ON user type record(praxis)"
        )
        
        logging.info(f"Create response: {create_response}")