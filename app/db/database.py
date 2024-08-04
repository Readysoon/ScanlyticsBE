from surrealdb import Surreal

import logging

async def initializedb():
    async with Surreal("ws://surrealdb:8000/rpc") as db:
        await db.signin({"user": "root", "pass": "root"})
        await db.use("test", "test")
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        create_response = await db.query(

            # User table 
            # -> users are doctors
            "DEFINE TABLE user schemafull;"
            "DEFINE FIELD mail on user TYPE string;"
            "DEFINE FIELD password on user TYPE string;"
            "DEFINE FIELD praxis ON user TYPE record(praxis);"

            # Practice table
            # -> doctors collaborate in practices
            "DEFINE FIELD in ON TABLE works_at TYPE record<user>;"
            "DEFINE FIELD out ON TABLE works_at TYPE record<praxis>;"

            "DEFINE TABLE praxis schemafull;"
            "DEFINE FIELD name ON praxis TYPE string;"

            # Patient table
            # -> doctors have patients
            "DEFINE FIELD in ON TABLE cares_for TYPE record<user>;"
            "DEFINE FIELD out ON TABLE cares_for TYPE record<patient>;"

            "DEFINE TABLE patient schemafull;"
            "DEFINE FIELD name ON patient TYPE string;"
            "DEFINE FIELD email ON patient TYPE string;"

            # Doctor_Report table
            # -> to enable the doctors to have their personal collection of templates with which they can replace ours 
            # -> in contrast to radreport_report which are the 433 report templates we take from radreport (or somewhere else)
            "DEFINE FIELD in ON TABLE writes TYPE record<user>;"
            "DEFINE FIELD out ON TABLE writes TYPE record<doctor_report>;"

            "DEFINE TABLE doctor_report schemafull;"
            "DEFINE FIELD name ON doctor_report TYPE string;"
            "DEFINE FIELD text ON doctor_report TYPE string;"

            # Radreport_Report table
            # -> in contrast this is our collection of reports, therefore not connected to the other tables (so far)
            "DEFINE TABLE radreport_report schemafull;"
            "DEFINE FIELD name ON radreport_report TYPE string;"
            "DEFINE FIELD text ON radreport_report TYPE string;"
        )
        
        logging.info(f"Create response: {create_response}")