from abc import ABC, abstractmethod
from typing import List
from database.crud_operation_base import CRUDOperationBase
from database.db_session import DBSession
from database.operations.toolwear_damage.toolwear_damage_operation_base import ToolWearDamageOperationBase
from models.model import ToolWearDamageDB 
from schemas.toolwear_damage import ToolWearDamageModel
from sqlalchemy import func, desc 

class ToolWearDamageOperation(ToolWearDamageOperationBase, CRUDOperationBase[ToolWearDamageDB]):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    def get_model_class(self):
        return ToolWearDamageDB
    
    def convert_to_db_object(self, data:ToolWearDamageModel)-> ToolWearDamageDB:
        return ToolWearDamageDB(**data.dict())

    def create_toolwear_damage(self, ml_model_data: ToolWearDamageModel):
        return self.create(ml_model_data)

    def get_toolwear_damage(self, tool_wear_damage_id: int) -> ToolWearDamageDB:
        return self.get(tool_wear_damage_id)

    def delete_toolwear_damage(self, tool_wear_damage_id: int):
        return self.delete(tool_wear_damage_id)

    def edit_toolwear_damage(self, tool_wear_damage_id: int, toolwear_model: ToolWearDamageModel) -> ToolWearDamageDB:
        return self.edit_by_key(tool_wear_damage_id, toolwear_model)
    
    def get_all_toolwear_damage_by_user_input_data_id_ordered(self, user_input_data_id) -> List[ToolWearDamageDB]:
        session = self.db_session.get_session()
        try:
            configs = session.query(self.get_model_class()).filter(ToolWearDamageDB.user_data_id == user_input_data_id).order_by(desc(self.get_model_class().created_at)).all()
            return configs
        finally:
            session.close()

    

