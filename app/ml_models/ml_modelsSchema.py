from pydantic import BaseModel, model_validator
from typing import Optional

class Model_IN(BaseModel):
    model_name: str


