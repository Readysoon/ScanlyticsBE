from pydantic import BaseModel
from typing import Optional

class Image(BaseModel):
    image_name: Optional[str] = None
#     date_of_birth: Optional[str] = None 
#     gender: Optional[str] = None
#     contact_number: Optional[str] = None
#     address: Optional[str] = None

# f"CREATE Image "
# f"SET name = '{file.filename}', "
# f"path = '{s3_url}', "
# f"body_type = 'arm', "
# f"modal_type = 'mri', "
# f"file_type = '{file_type}', "
# f"patient = 'Patient:{patient_id}', "
# f"user = '{current_user_id}'"
# '''update image'''