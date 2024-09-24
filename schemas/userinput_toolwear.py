from pydantic import BaseModel, ValidationError, validator
from datetime import datetime
from typing import Optional

class UserInputToolWearModel(BaseModel):
    werkstoff: str
    definierter_vbmax_value: Optional[float]
    definierter_vbmax_unit: Optional[str]
    schnittgeschwindigkeit_value: Optional[float]
    schnittgeschwindigkeit_unit: Optional[str]
    vorschub_value: Optional[float]
    vorschub_unit: Optional[str]
    schnitttiefe_value: Optional[float]
    schnitttiefe_unit: Optional[str]
    kühlung: str
    werkzeugtyp: Optional[str]
    schneidstoff: Optional[str]
    schneide: Optional[str]
    beschichtung: Optional[str]
    surface: str
    images_folder: str
    created_at: datetime
    created_by:int 

    @validator("definierter_vbmax_value", "schnittgeschwindigkeit_value", "vorschub_value", "schnitttiefe_value")
    def validate_numerical_values(cls, value):
        if not isinstance(value, (int, float)):
            raise ValueError("Value must be a numerical value.")
        return value

    @classmethod
    def from_widget_data(cls, **kwargs):
        try:
            return cls(**kwargs)
        except ValidationError as e:
            # Handle validation errors
            raise ValueError(str(e)) from None  # Raise a more general error instead of displaying QMessageBox
