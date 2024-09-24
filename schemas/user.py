from pydantic import BaseModel
from typing import Optional

class UserModel(BaseModel):
    id: Optional[int] 
    name: str
    password: str
    is_admin: bool = False
    label_studio_api_key: Optional[str] = None
