from abc import ABC, abstractmethod
from typing import List
from database.db_session import DBSession
from schemas.toolwear_damage import ToolWearDamageModel
from models.model import ToolWearDamageDB 

class ToolWearDamageOperationBase(ABC):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    @abstractmethod
    def create_toolwear_damage(self, ml_model_data: ToolWearDamageModel):
        pass

    @abstractmethod
    def convert_to_db_object(self, data:ToolWearDamageModel)-> ToolWearDamageDB:
        pass

    @abstractmethod
    def get_toolwear_damage(self, tool_wear_damage_id: int) -> ToolWearDamageModel:
        pass

    @abstractmethod
    def delete_toolwear_damage(self, tool_wear_damage_id: int):
        pass

    @abstractmethod
    def edit_toolwear_damage(self, tool_wear_damage_id: int, toolwear_model: ToolWearDamageModel) -> ToolWearDamageDB:
        pass

    @abstractmethod
    def get_all_toolwear_damage_by_user_input_data_id_ordered(self, user_input_data_id) -> List[ToolWearDamageDB]:
        pass 

    