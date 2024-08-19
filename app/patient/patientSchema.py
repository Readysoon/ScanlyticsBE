from pydantic import BaseModel

class CreatePatient(BaseModel):
    patient_name: str
    # date_of_birth has to be str in order to be processable by SurrealDB
    date_of_birth: str
    gender: str
    contact_number: str
    address: str