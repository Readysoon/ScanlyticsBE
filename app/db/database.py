from surrealdb import Surreal

import logging

async def initializedb():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        create_response = await db.query(
            "DEFINE TABLE praxis schemafull;"
            "DEFINE FIELD name on praxis type string;"

            "DEFINE FIELD in ON TABLE works_at TYPE record<user>;"
            "DEFINE FIELD out ON TABLE works_at TYPE record<praxis>;"

            "DEFINE TABLE user schemafull;"
            "DEFINE FIELD mail on user type string;"
            "DEFINE FIELD password on user type string;"
            "DEFINE FIELD praxis ON user type record(praxis);"

            "DEFINE FIELD in ON TABLE treats TYPE record<user>;"
            "DEFINE FIELD out ON TABLE treats TYPE record<patient>;"

            "DEFINE FIELD name on patient type string;"
        )
        
        logging.info(f"Create response: {create_response}")