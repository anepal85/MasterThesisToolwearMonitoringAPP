from typing import List
from database.crud_operation_base import CRUDOperationBase
from database.db_session import DBSession
from database.operations.ml_model.ml_model_operation_base import MLModelOperationBase
from schemas.ml_model import MLModel
from models.model import MLModelDB

class MLModelOperation(MLModelOperationBase, CRUDOperationBase[MLModelDB]):
    def __init__(self, db_session: DBSession):
        super().__init__(db_session)

    def get_model_class(self):
        return MLModelDB
    
    def convert_to_db_object(self, data: MLModel) -> MLModelDB:
        db_data = data.dict()
        db_data.pop('id', None)
        return MLModelDB(**db_data)
    
    def convert_db_model_to_pydantic(self, db_model: MLModelDB) -> MLModel:
        return MLModel(
            id=db_model.id,
            name=db_model.name,
            ml_model_path=db_model.ml_model_path,
            epochs_trained=db_model.epochs_trained,
            input_im_width=db_model.input_im_width,
            input_im_height=db_model.input_im_height,
            created_at=db_model.created_at
        )
    
    def create_ml_model(self, ml_model_data: MLModel):
        return self.create(ml_model_data)

    def delete_ml_model(self, ml_model_id: int):
        return self.delete(ml_model_id)

    def edit_model(self, ml_model_id: int, ml_model_data: MLModel):
        return self.edit_by_key(ml_model_id, ml_model_data)

    def get_ml_model(self, ml_model_id: int) -> MLModelDB:
        return self.get(ml_model_id)
    
    def get_by_name(self, ml_modelname: str) -> MLModelDB:
        session = self.db_session.get_session()
        try:
            model_class = self.get_model_class()
            object_instance = session.query(model_class).filter(model_class.name == ml_modelname).first()
            return object_instance
        finally:
            session.close()
    
    def get_all_mlmodel(self) -> List[MLModelDB]:
        """Retrieve all ML models from the database."""
        return self.get_all()