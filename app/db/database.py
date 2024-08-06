import os
import logging
from surrealdb import Surreal

DATABASE_URL = os.getenv("SURREALDB_URL", "ws://surrealdb:8000/rpc")

async def get_db():
    logging.info(f"Attempting to connect to SurrealDB at {DATABASE_URL}")
    
    try:
        db = Surreal(DATABASE_URL)
        logging.info("Created SurrealDB instance")
        
        await db.connect()
        logging.info("Connected to SurrealDB")
        
        await db.signin({"user": "root", "pass": "root"})
        logging.info("Signed in to SurrealDB")
        
        await db.use("test", "test")
        logging.info("Using database 'test' and namespace 'test'")
        
        yield db
    except Exception as e:
        logging.error(f"Error connecting to SurrealDB: {e}")
        raise e
    finally:
        await db.close()
        logging.info("Closed SurrealDB connection")

