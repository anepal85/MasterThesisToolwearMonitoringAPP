from database.crud_operation_base import CRUDOperationBase
from database.db_session import DBSession
from database.operations.dino_image.dino_image_operation_base import DinoImageOperationBase
from schemas.dino_image import DinoImageModel
from models.model import DinoImageDB

class DinoImageOperation(DinoImageOperationBase, CRUDOperationBase[DinoImageDB]):
    def __init__(self, db_session: DBSession):
        super().__init__(db_session)

    def get_model_class(self):
        return DinoImageDB
    
    def convert_to_db_object(self, data: DinoImageModel) -> DinoImageDB:
        return DinoImageDB(**data.dict())
    
    def create_dino_image(self, ml_model_data: DinoImageModel):
        return self.create(ml_model_data)

    def delete_dino_image(self, ml_model_id: int):
        return self.delete(ml_model_id)

    def edit_dino_image(self, ml_model_id: int, ml_model_data: DinoImageModel):
        return self.edit_by_key(ml_model_id, ml_model_data)

    def get_dino_image(self, ml_model_id: int) -> DinoImageDB:
        return self.get(ml_model_id)
