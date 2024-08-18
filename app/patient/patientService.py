from surrealdb import Surreal
from pydantic import BaseModel

import logging

async def CreatePatientService():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        praxisObject = await db.query(f"CREATE praxis:diagnostikum SET name = 'diagnostikum';")

        print("trying out praxis Service")
        print(praxisObject)

        # create_response = await db.query(
        #         f"CREATE user SET mail = 'haha@gmail.com', password = '1234', praxis = praxis:diagnostikum;"
        #     )
        # 
        # logging.info(f"Create response: {create_response}")