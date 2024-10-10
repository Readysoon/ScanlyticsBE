from pydantic import BaseModel
from typing import Optional, List

class Report(BaseModel):
    body_part: Optional[str] = None
    condition: Optional[str] = None
    report_text: Optional[str] = None
    patient_id: Optional[str] = None
    image_id_array: Optional[List[str]] = None
