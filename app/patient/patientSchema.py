from pydantic import BaseModel
from typing import Optional

class CreatePatient(BaseModel):
    patient_name: Optional[str] = None
    date_of_birth: Optional[str] = None 
    gender: Optional[str] = None
    contact_number: Optional[str] = None
    address: Optional[str] = None