from abc import ABC, abstractmethod
from typing import List
from database.db_session import DBSession
from schemas.ml_model import MLModel
from models.model import MLModelDB 

class MLModelOperationBase(ABC):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    @abstractmethod
    def create_ml_model(self, ml_model_data: MLModel):
        pass

    @abstractmethod
    def convert_to_db_object(self, data:MLModel)-> MLModelDB:
        pass
    @abstractmethod
    def convert_db_model_to_pydantic(self, db_model: MLModelDB) -> MLModel:
        pass 

    @abstractmethod
    def get_ml_model(self, ml_model_id: int) -> MLModel:
        pass

    @abstractmethod
    def delete_ml_model(self, ml_model_id: int):
        pass

    @abstractmethod
    def edit_model(self, user_id: int, user_data: MLModel) -> MLModelDB:
        pass

    @abstractmethod
    def get_all_mlmodel(self) -> List[MLModelDB]:
        pass #

    @abstractmethod
    def get_by_name(self, ml_modelname: str) -> MLModelDB:
        pass 
