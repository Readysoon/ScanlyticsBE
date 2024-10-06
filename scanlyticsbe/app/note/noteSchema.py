from pydantic import BaseModel
from typing import Optional

from pydantic import BaseModel, model_validator


'''Change from Optional to not optional after finding out ;)'''
'''Severity: Research choosing from Options'''

class Note(BaseModel):
    symptoms: str = None
    diagnosis: Optional[str] = None 
    treatment: Optional[str] = None
    severity: Optional[str] = None #implement choosing from options here -> enum -> DOCS
    is_urgent: Optional[bool] = None
    patient: Optional[str] = None

    # @model_validator(mode='before')
    # def validate_note(cls, values):
    #     if all(value is None for value in values.values()):
    #         raise ValueError("At least one parameter must be provided")
    #     return values
