from pydantic import BaseModel
from typing import List, EmailStr

class EmailSchema(BaseModel):
    email: List[EmailStr]