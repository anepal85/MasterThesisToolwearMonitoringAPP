from typing import Optional
from database.crud_operation_base import CRUDOperationBase
from database.db_session import DBSession
from database.operations.user.user_operation_base import UserOperationBase
from models.model import UserDB as User 
from schemas.user import UserModel 


class UserOperation(UserOperationBase, CRUDOperationBase[User]):
    def __init__(self, db_session: DBSession):
        super().__init__(db_session)

    def get_model_class(self):
        return User
    
    def convert_to_db_object(self, data: UserModel) -> User:
        user_data = data.dict()
        user_data.pop('id', None)
        return User(**user_data)

    def create_user(self, user_data: User):
        return self.create(user_data)

    def get_user(self, user_id: int) -> User:
        return self.get(user_id)
    
    def get_user_by_name(self, username: str) -> Optional[User]:
        session = self.db_session.get_session()
        user = None
        try:
            user = session.query(User).filter(User.name == username).first()
        finally:
            session.close()
        return user
    
    def delete_user(self, user_id: int):
        return self.delete(user_id)

    def edit_user(self, user_id: int, user_data: UserModel) -> User:
        return self.edit_by_key(user_id, user_data)
    
    def update_api_key(self, user_id: int, api_key: str) -> User:
        session = self.db_session.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.label_studio_api_key = api_key
                session.commit()
        finally:
            session.close()
        return user
    
    