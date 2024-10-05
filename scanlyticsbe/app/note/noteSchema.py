from pydantic import BaseModel
from typing import Optional

'''Change from Optional to not optional after finding out ;)'''
'''Severity: Research choosing from Options'''

class Note(BaseModel):
    symptoms: Optional[str] = None
    diagnosis: Optional[str] = None 
    treatment: Optional[str] = None
    severity: Optional[str] = None
    is_urgent: Optional[bool] = None