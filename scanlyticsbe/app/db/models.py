from .database import get_db
from fastapi import HTTPException, status

import logging

'''implement access rights '''
'''body_type -> Report still needs to be fixed'''
'''Options for user roles'''

async def initializedb():
    async for db in get_db():
        logging.info("Connected to SurrealDB with namespace 'test' and database 'test'")

        # Add default Organisation:1 for independent doctors?

        surreal_command_list = [
            "DEFINE TABLE Organization SCHEMAFULL;",
            "DEFINE FIELD name ON Organization TYPE string;",
            "DEFINE FIELD address ON Organization TYPE string;",
            "DEFINE FIELD email ON Organization TYPE string ASSERT string::is::email($value);",
            "DEFINE FIELD created_at ON Organization TYPE datetime DEFAULT time::now();",
            "DEFINE FIELD updated_at ON Organization TYPE datetime DEFAULT time::now() VALUE time::now();",
            "DEFINE FIELD user ON Organization TYPE option<array>;",
            "DEFINE FIELD user.* ON Organization TYPE option<record(User)>;",

            "DEFINE TABLE User SCHEMAFULL;",
            "DEFINE FIELD name ON User TYPE string;",
            "DEFINE FIELD email ON User TYPE string ASSERT string::is::email($value);",
            "DEFINE FIELD password ON User TYPE string;",
            "DEFINE FIELD role ON User TYPE string;",
            "DEFINE FIELD created_at ON User TYPE datetime DEFAULT time::now();",
            "DEFINE FIELD updated_at ON User TYPE datetime DEFAULT time::now() VALUE time::now();",
            "DEFINE FIELD notes ON User TYPE option<array>;",
            "DEFINE FIELD notes.* ON User TYPE option<record(PatientNote)>;",
            "DEFINE FIELD Statement ON User TYPE option<array>;",
            "DEFINE FIELD Statement.* ON User TYPE option<record(Statement)>;",
            "DEFINE FIELD Image ON User TYPE option<array>;",
            "DEFINE FIELD Image.* ON User TYPE option<record(Image)>;",
            "DEFINE FIELD organization ON User TYPE record(Organization);",
            "DEFINE FIELD in ON TABLE Write_Reports TYPE record<User>;",
            "DEFINE FIELD out ON TABLE Write_Reports TYPE record<Report>;",
            "DEFINE FIELD in ON TABLE Access_Statements TYPE record<User>;",
            "DEFINE FIELD out ON TABLE Access_Statements TYPE record<Statement>;",

            "DEFINE TABLE Patient SCHEMAFULL;",
            "DEFINE FIELD name ON Patient TYPE string;",
            "DEFINE FIELD date_of_birth ON Patient TYPE datetime;",
            "DEFINE FIELD gender ON Patient TYPE string;",
            "DEFINE FIELD contact_number ON Patient TYPE string;",
            "DEFINE FIELD address ON Patient TYPE string;",
            "DEFINE FIELD created_at ON Patient TYPE datetime DEFAULT time::now();",
            "DEFINE FIELD updated_at ON Patient TYPE datetime DEFAULT time::now() VALUE time::now();",
            "DEFINE FIELD notes ON Patient TYPE option<array>;",
            "DEFINE FIELD notes.* ON Patient TYPE option<record(PatientNote)>;",
            "DEFINE FIELD report ON Patient TYPE option<array>;",
            "DEFINE FIELD report.* ON Patient TYPE option<record(Report)>;",
            "DEFINE FIELD image ON Patient TYPE option<array>;",
            "DEFINE FIELD image.* ON Patient TYPE option<record(Image)>;",
            "DEFINE FIELD out ON TABLE Treated_By TYPE record<User>;",
            "DEFINE FIELD in ON TABLE Treated_By TYPE record<Patient>;",

            "DEFINE TABLE PatientNote SCHEMAFULL;",
            "DEFINE FIELD symptoms ON PatientNote TYPE string;",
            "DEFINE FIELD diagnosis ON PatientNote TYPE string;",
            "DEFINE FIELD treatment ON PatientNote TYPE string;",
            "DEFINE FIELD created_at ON PatientNote TYPE datetime DEFAULT time::now();",
            "DEFINE FIELD updated_at ON PatientNote TYPE datetime DEFAULT time::now() VALUE time::now();",
            "DEFINE FIELD severity ON PatientNote TYPE string ASSERT $value IN ['low', 'medium', 'high'];",
            "DEFINE FIELD is_urgent ON PatientNote TYPE bool;",
            "DEFINE FIELD patient ON PatientNote TYPE record(Patient);",
            "DEFINE FIELD user_owner ON PatientNote TYPE record(User);",
            "DEFINE FIELD out ON TABLE PatientNotes_Reports_Join TYPE record<User>;",
            "DEFINE FIELD in ON TABLE PatientNotes_Reports_Join TYPE record<PatientNote>;",

            "DEFINE TABLE Statement SCHEMAFULL;",
            "DEFINE FIELD text ON Statement TYPE array<string>;",
            "DEFINE FIELD body_part ON Statement TYPE string;",
            "DEFINE FIELD medical_condition ON Statement TYPE string;",
            "DEFINE FIELD modality ON Statement TYPE string;",
            "DEFINE FIELD section ON Statement TYPE string;",
            "DEFINE FIELD created_at ON Statement TYPE datetime DEFAULT time::now();",
            "DEFINE FIELD updated_at ON Statement TYPE datetime DEFAULT time::now() VALUE time::now();",
            "DEFINE FIELD user_owner ON Statement TYPE record(User);",

            "DEFINE TABLE Report SCHEMAFULL;",
            "DEFINE FIELD body_type ON Report TYPE string;",
            "DEFINE FIELD condition ON Report TYPE string;",
            "DEFINE FIELD report_text ON Report TYPE string;",
            "DEFINE FIELD created_at ON Report TYPE datetime DEFAULT time::now();",
            "DEFINE FIELD updated_at ON Report TYPE datetime DEFAULT time::now() VALUE time::now();",
            "DEFINE FIELD in ON TABLE Statements_Reports_Join TYPE record<Statement>;",
            "DEFINE FIELD out ON TABLE Statements_Reports_Join TYPE record<Report>;",
            "DEFINE FIELD patient ON Report TYPE record(Patient);",

            "DEFINE TABLE Image SCHEMAFULL;",
            "DEFINE FIELD name ON Image TYPE string;",
            "DEFINE FIELD path ON Image TYPE string;",
            "DEFINE FIELD body_part ON Image TYPE string;",
            "DEFINE FIELD modality ON Image TYPE string ASSERT $value IN ['xray', 'mri', 'ct'];",
            "DEFINE FIELD file_type ON Image TYPE string;",
            "DEFINE FIELD created_at ON Image TYPE datetime DEFAULT time::now();",
            "DEFINE FIELD updated_at ON Image TYPE datetime DEFAULT time::now() VALUE time::now();",
            "DEFINE FIELD patient ON Image TYPE record(Patient);",
            "DEFINE FIELD user ON Image TYPE record(User);",
            "DEFINE FIELD in ON TABLE Images_Reports_Join TYPE record<Image>;",
            "DEFINE FIELD out ON TABLE Images_Reports_Join TYPE record<Report>;",

            "DEFINE INDEX Patients_Reports_Join ON TABLE Treated_By COLUMNS in, out UNIQUE;",
            "DEFINE INDEX Treated_By ON TABLE Treated_By COLUMNS in, out UNIQUE;",
            "DEFINE INDEX Access_Statements ON TABLE Access_Statements COLUMNS in, out UNIQUE;",
            "DEFINE INDEX Patients_Reports_Join ON TABLE Patients_Reports_Join COLUMNS in, out UNIQUE;",
            "DEFINE INDEX PatientNotes_Reports_Join ON TABLE PatientNotes_Reports_Join COLUMNS in, out UNIQUE;",
            "DEFINE INDEX Statements_Reports_Join ON TABLE Statements_Reports_Join COLUMNS in, out UNIQUE;",
            "DEFINE INDEX Images_Reports_Join ON TABLE Images_Reports_Join COLUMNS in, out UNIQUE;",
            "DEFINE INDEX Write_Reports ON TABLE Write_Reports COLUMNS in, out UNIQUE;",
            "DEFINE INDEX Email ON TABLE Organization COLUMNS email UNIQUE;",
            "DEFINE INDEX Email ON TABLE User COLUMNS email UNIQUE;",

            "DEFINE TABLE Treated_By SCHEMAFULL;",
            "DEFINE TABLE Patients_Reports_Join SCHEMAFULL;",
            "DEFINE TABLE Access_Statements SCHEMAFULL;",
            "DEFINE TABLE PatientNotes_Reports_Join SCHEMAFULL;",
            "DEFINE TABLE Statements_Reports_Join SCHEMAFULL;",
            "DEFINE TABLE Images_Reports_Join SCHEMAFULL;",
            "DEFINE TABLE Write_Reports SCHEMAFULL;",
        ]

        for command in surreal_command_list:
            try:
                await db.query(command)
            except Exception as e:
                raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=
                                    f"Error in database initialization during command: {command}, Error: {e}")

