import os
import logging
from surrealdb import Surreal
from dotenv import load_dotenv
from fastapi import status

from app.error.errorService import ErrorStack

# Load environment variables from the .env file
load_dotenv()

DATABASE_URL = os.getenv("SURREALDB_URL")
DATABASE_USER = os.getenv("SURREALDB_USER")
DATABASE_PASS = os.getenv("SURREALDB_PASS")
DATABASE_NAMESPACE = os.getenv("SURREALDB_NAMESPACE")
DATABASE_NAME = os.getenv("SURREALDB_DATABASE")

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


def DatabaseResultService(query_result):
    error_stack = ErrorStack()

    if not query_result[0]['result']:
        print(f"{DatabaseResultService.__name__}: if not query_result[0]['result']:")
        error_stack.add_error(status.HTTP_404_NOT_FOUND, "No Result found.", DatabaseResultService.__name__)
        print(error_stack)

    if query_result[0]['status'] == 'ERR':
        result = query_result[0]['result']
        error_stack.add_error(status.HTTP_500_INTERNAL_SERVER_ERROR, f"Status == 'ERR': {result}", DatabaseResultService.__name__)

    return error_stack