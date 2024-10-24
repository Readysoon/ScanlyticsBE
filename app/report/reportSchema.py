from pydantic import BaseModel
from typing import Optional, List

'''array for statements'''
class Report(BaseModel):
    body_part: Optional[str] = None
    condition: Optional[str] = None
    report_text: Optional[str] = None
    patient_id: Optional[str] = None
    statement_id_array: Optional[List[str]] = []
    image_id_array: Optional[List[str]] = None
