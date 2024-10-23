from pydantic import BaseModel, model_validator
from typing import Optional


class Model(BaseModel):
    name: str
    version: str
    category: str
    link: str
    description: Optional[str]


