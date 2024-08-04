from surrealdb import Surreal

import logging

async def initializedb():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        create_response = await db.query(
            "DEFINE TABLE user schemafull;"
            "DEFINE FIELD mail on user TYPE string;"
            "DEFINE FIELD password on user TYPE string;"
            "DEFINE FIELD praxis ON user TYPE record(praxis);"

            # Practice table
            "DEFINE FIELD in ON TABLE works_at TYPE record<user>;"
            "DEFINE FIELD out ON TABLE works_at TYPE record<praxis>;"

            "DEFINE TABLE praxis schemafull;"
            "DEFINE FIELD name ON praxis TYPE string;"

            # Patient table
            "DEFINE FIELD in ON TABLE cares_for TYPE record<user>;"
            "DEFINE FIELD out ON TABLE cares_for TYPE record<patient>;"

            "DEFINE TABLE patient schemafull;"
            "DEFINE FIELD name ON patient TYPE string;"
            "DEFINE FIELD email ON patient TYPE string;"

            


        )
        
        logging.info(f"Create response: {create_response}")