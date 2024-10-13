from pydantic import BaseModel
from typing import Optional, List

class Images(BaseModel):
    image_id_array: Optional[List[str]] = None