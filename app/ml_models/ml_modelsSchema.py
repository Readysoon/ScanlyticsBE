from pydantic import BaseModel, model_validator

class Model_IN(BaseModel):
    model_name: str


