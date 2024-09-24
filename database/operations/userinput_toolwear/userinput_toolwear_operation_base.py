from abc import ABC, abstractmethod
from typing import List
from database.db_session import DBSession
from schemas.userinput_toolwear import UserInputToolWearModel
from models.model import UserInputToolWearDB

class UserInputToolWearOperationBase(ABC):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    @abstractmethod
    def create_user_input_data(self, user_input_data: UserInputToolWearModel):
        pass

    @abstractmethod
    def convert_to_db_object(self, data: UserInputToolWearModel) -> UserInputToolWearDB:
        pass

    @abstractmethod
    def get_user_input_data(self, user_input_data_id: int) -> UserInputToolWearModel:
        pass

    @abstractmethod
    def delete_user_input_data(self, user_input_data_id: int):
        pass

    @abstractmethod
    def edit_user_input_data(self, user_input_data_id: int, user_input_data: UserInputToolWearModel) -> UserInputToolWearDB:
        pass
    
    @abstractmethod
    def get_all_configs_ordered(self) -> List[UserInputToolWearDB]:
        pass 
