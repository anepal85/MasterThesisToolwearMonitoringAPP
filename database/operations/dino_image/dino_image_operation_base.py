from abc import ABC, abstractmethod
from database.db_session import DBSession
from schemas.dino_image import DinoImageModel
from models.model import DinoImageDB

class DinoImageOperationBase(ABC):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    @abstractmethod
    def create_dino_image(self, ml_model_data: DinoImageModel):
        pass

    @abstractmethod
    def convert_to_db_object(self, data:DinoImageModel)-> DinoImageDB:
        pass

    @abstractmethod
    def get_dino_image(self, ml_model_id: int) -> DinoImageModel:
        pass

    @abstractmethod
    def delete_dino_image(self, ml_model_id: int):
        pass

    @abstractmethod
    def edit_dino_image(self, user_id: int, user_data: DinoImageModel) -> DinoImageDB:
        pass
