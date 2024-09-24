from pydantic import BaseModel
from typing import Optional

class Report(BaseModel):
    body_type: Optional[str] = None
    condition: Optional[str] = None
    report_text: Optional[str] = None