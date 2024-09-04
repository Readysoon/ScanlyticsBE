from surrealdb import Surreal
import asyncio

import logging


SURREALDB_URL = ''

async def test_db_connection():
    async with Surreal("wss://surrealdb-deployment-floral-meadow-3035.fly.dev/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")
        print("Connected to SurrealDB with namespace 'test' and database 'test'")

        # Perform a test insertion
        test_data = {
            "name": "John Doe",
            "email": "johndoe@example.com"
        }
        created_record = await db.create("person", test_data)
        
        # Log the result of the insertion
        logging.info(f"Inserted record: {created_record}")
        print(f"Inserted record: {created_record}")

def main():
    asyncio.run(test_db_connection())

if __name__ == "__main__":
    main()
