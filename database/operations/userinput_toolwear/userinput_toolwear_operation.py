from typing import List
from database.crud_operation_base import CRUDOperationBase
from database.db_session import DBSession
from database.operations.userinput_toolwear.userinput_toolwear_operation_base import UserInputToolWearOperationBase
from models.model import UserInputToolWearDB 
from schemas.userinput_toolwear import UserInputToolWearModel 
from sqlalchemy import desc, func 

class UserInputToolWearOperation(UserInputToolWearOperationBase, CRUDOperationBase[UserInputToolWearDB]):
    def __init__(self, db_session: DBSession):
        super().__init__(db_session)

    def get_model_class(self):
        return UserInputToolWearDB

    def convert_to_db_object(self, data: UserInputToolWearModel) -> UserInputToolWearDB:
        user_input_data = data.dict()
        user_input_data.pop('id', None)
        return UserInputToolWearDB(**user_input_data)
    
    def db_to_pydantic(self, user_input_tool_wear_db):
        pydantic_data = user_input_tool_wear_db.__dict__
        return UserInputToolWearModel(**pydantic_data)

    def create_user_input_data(self, user_input_data: UserInputToolWearDB):
        return self.create(user_input_data)

    def get_user_input_data(self, user_input_data_id: int) -> UserInputToolWearDB:
        return self.get(user_input_data_id)

    def delete_user_input_data(self, user_input_data_id: int):
        return self.delete(user_input_data_id)

    def edit_user_input_data(self, user_input_data_id: int, user_input_data: UserInputToolWearModel) -> UserInputToolWearDB:
        return self.edit_by_key(user_input_data_id, user_input_data)
    
    def get_all_configs_ordered(self) -> List[UserInputToolWearDB]:
        session = self.db_session.get_session()
        try:
            configs = session.query(self.get_model_class()).order_by(desc(self.get_model_class().created_at)).all()
            return configs
        finally:
            session.close()

    def get_unique_column_values(self, column_name: str) -> List[str]:
        session = self.db_session.get_session()
        try:
            column = getattr(self.get_model_class(), column_name)
            unique_values = session.query(func.distinct(column)).all()
            return [value[0] for value in unique_values if value[0] is not None]
        finally:
            session.close()
    