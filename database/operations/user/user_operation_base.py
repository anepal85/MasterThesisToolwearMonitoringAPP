from abc import ABC, abstractmethod
from database.db_session import DBSession
from schemas.user import UserModel  
from models.model import UserDB 

class UserOperationBase(ABC):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    @abstractmethod
    def create_user(self, user_data: UserModel):
        pass

    @abstractmethod
    def convert_to_db_object(self, data:UserModel)-> UserDB:
        pass

    @abstractmethod
    def get_user(self, user_id: int) -> UserModel:
        pass

    @abstractmethod
    def delete_user(self, user_id: int):
        pass

    @abstractmethod
    def edit_user(self, user_id: int, user_data: UserModel) -> UserDB:
        pass
