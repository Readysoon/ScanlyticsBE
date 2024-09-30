from pydantic import BaseModel
from typing import Optional

class Image(BaseModel):
    image_name: Optional[str] = None
    body_part: Optional[str] = None
    modality: Optional[str] = None