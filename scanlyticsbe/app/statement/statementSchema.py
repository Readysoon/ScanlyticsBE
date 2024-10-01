from pydantic import BaseModel
from typing import Optional

#             "DEFINE TABLE Statement SCHEMAFULL;",
#             "DEFINE FIELD text ON Statement TYPE string;",
#             "DEFINE FIELD body_part ON Statement TYPE string;",
#             "DEFINE FIELD medical_condition ON Statement TYPE string;",
#             "DEFINE FIELD modality ON Statement TYPE string;",
#             "DEFINE FIELD section ON Statement TYPE string;",
#             "DEFINE FIELD created_at ON Statement TYPE datetime DEFAULT time::now();",
#             "DEFINE FIELD updated_at ON Statement TYPE datetime DEFAULT time::now() VALUE time::now();",
#             "DEFINE FIELD user_owner ON Statement TYPE record(User);",


class Statement(BaseModel):
    text: Optional[str] = None
    body_part: Optional[str] = None
    medical_condition: Optional[str] = None
    modality: Optional[str] = None
    section: Optional[str] = None