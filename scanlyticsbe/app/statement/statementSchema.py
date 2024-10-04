from pydantic import BaseModel
from typing import Optional


class Statement(BaseModel):
    text: Optional[str] = None
    body_part: Optional[str] = None
    medical_condition: Optional[str] = None
    modality: Optional[str] = None
    section: Optional[str] = None