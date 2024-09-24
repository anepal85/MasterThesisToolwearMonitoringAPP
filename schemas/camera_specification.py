from pydantic import BaseModel
from typing import List, Optional, Tuple

class CameraSpecs(BaseModel):
    magnification: float
    field_of_view: Optional[List[Tuple[float, float]]] = None
