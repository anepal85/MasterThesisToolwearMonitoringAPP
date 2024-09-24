from abc import ABC, abstractmethod
from database.db_session import DBSession
from typing import List, TypeVar, Generic, Any 

T = TypeVar('T')

class CRUDOperationBase(Generic[T], ABC):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    @abstractmethod
    def get_model_class(self)->Any:
        pass

    @abstractmethod
    def convert_to_db_object(self, data: T)->Any:
        pass

    def create(self, data: T) -> T:
        session = self.db_session.get_session()
        try:
            new_object = self.convert_to_db_object(data)
            session.add(new_object)
            session.commit()
            session.refresh(new_object)
            return new_object
        finally:
            session.close()

    def get(self, object_id: int) -> T:
        session = self.db_session.get_session()
        try:
            object_instance = session.query(self.get_model_class()).filter(self.get_model_class().id == object_id).first()
            return object_instance
        finally:
            session.close()

    def delete(self, object_id: int):
        session = self.db_session.get_session()
        try:
            object_instance = session.query(self.get_model_class()).filter(self.get_model_class().id == object_id).first()
            if object_instance:
                session.delete(object_instance)
                session.commit()
        finally:
            session.close()
            
    def edit_by_key(self, object_id: int, data: T) -> T:
        session = self.db_session.get_session()
        try:
            object_instance = session.query(self.get_model_class()).filter(self.get_model_class().id == object_id).first()
            if object_instance:
                self.convert_to_db_object(data)
                session.commit()
            return object_instance
        finally:
            session.close
    
    def get_all(self) -> List[T]:
        session = self.db_session.get_session()
        try:
            objects = session.query(self.get_model_class()).all()
            return objects
        except Exception as e:
            raise e
        finally:
            session.close()



# from abc import ABC, abstractmethod
# from database.db_session import DBSession
# from typing import TypeVar, Generic, Any 

# T = TypeVar('T')

# class CRUDOperationBase(Generic[T], ABC):
#     def __init__(self, db_session: DBSession):
#         self.db_session = db_session

#     @abstractmethod
#     def get_model_class(self) -> Any:
#         pass

#     @abstractmethod
#     def convert_to_db_object(self, data: T) -> Any:
#         pass

#     def __enter__(self):
#         self.session = self.db_session.get_session()
#         return self

#     def __exit__(self, exc_type, exc_value, traceback):
#         self.session.close()

#     def create(self, data: T) -> T:
#         new_object = self.convert_to_db_object(data)
#         self.session.add(new_object)
#         self.session.commit()
#         return new_object

#     def get(self, object_id: int) -> T:
#         return self.session.query(self.get_model_class()).filter(self.get_model_class().id == object_id).first()

#     def delete(self, object_id: int):
#         object_instance = self.session.query(self.get_model_class()).filter(self.get_model_class().id == object_id).first()
#         if object_instance:
#             self.session.delete(object_instance)
#             self.session.commit()

#     def edit_by_key(self, object_id: int, data: T) -> T:
#         object_instance = self.session.query(self.get_model_class()).filter(self.get_model_class().id == object_id).first()
#         if object_instance:
#             self.convert_to_db_object(data)
#             self.session.commit()
#         return object_instance
