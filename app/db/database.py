import os
import logging
from surrealdb import Surreal

DATABASE_URL = os.getenv("SURREALDB_URL", "ws://surrealdb:8000/rpc")
DATABASE_USER = os.getenv("SURREALDB_USER", "root")
DATABASE_PASS = os.getenv("SURREALDB_PASS", "root")
DATABASE_NAMESPACE = os.getenv("SURREALDB_NAMESPACE", "test")
DATABASE_NAME = os.getenv("SURREALDB_DATABASE", "test")

async def get_db():
    logging.info(f"Attempting to connect to SurrealDB at {DATABASE_URL}")

    try:
        db = Surreal(DATABASE_URL)
        logging.info("Created SurrealDB instance")
        
        await db.connect()
        logging.info("Connected to SurrealDB")
        
        await db.signin({"user": DATABASE_USER, "pass": DATABASE_PASS})
        logging.info("Signed in to SurrealDB")
        
        await db.use(DATABASE_NAMESPACE, DATABASE_NAME)
        logging.info(f"Using namespace '{DATABASE_NAMESPACE}' and database '{DATABASE_NAME}'")
        
        yield db
    except Exception as e:
        logging.error(f"Error connecting to SurrealDB: {e}")
        raise e
    finally:
        await db.close()
        logging.info("Closed SurrealDB connection")
