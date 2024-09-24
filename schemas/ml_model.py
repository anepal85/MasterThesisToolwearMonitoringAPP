from typing import Optional
from pydantic import BaseModel, validator
from pathlib import Path
from datetime import datetime 

class MLModel(BaseModel):
    id: Optional[int] = None 
    name: str
    ml_model_path: str
    epochs_trained: int = 200
    input_im_width: int = 512
    input_im_height: int = 512
    created_at: datetime  


    @validator('ml_model_path')
    def check_mlmodel_path_exists(cls, value):
        if not Path(value).is_file():
            raise ValueError(f"File does not exist at path: {value}")
        return value


