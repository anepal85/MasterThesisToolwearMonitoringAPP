from pydantic import BaseModel
from typing import Optional
from datetime import datetime 

class DinoImageModel(BaseModel):
    id: Optional[int] = None 
    toolwear_damage_id: int 
    image_path: str
    magnification: float
    fovx: float
    fovy: float
    created_at: datetime  