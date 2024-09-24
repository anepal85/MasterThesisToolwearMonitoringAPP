from typing import Optional
from pydantic import BaseModel, ValidationError, validator
from pathlib import Path
from datetime import datetime

class ToolWearDamageModel(BaseModel):
    id: Optional[int] = None 
    ml_model_id: int
    user_id: int
    user_data_id : int 
    damage_area_pixel: int
    damage_area: float 
    damage_up: float
    damage_down: float
    process_number: int 
    is_manual: bool  
    y_algo: int 
    y_manual : int  
    created_at: datetime  
    correct_prediction:bool = True 

    # @field_validator('images_folder')
    # def check_image_path_exists(cls, value):
    #     if not Path(value).is_dir():
    #         raise ValueError(f"Folder does not exist at path: {value}")
    #     return value

    
