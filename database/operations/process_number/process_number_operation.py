from typing import Optional

from sqlalchemy import func
from database.crud_operation_base import CRUDOperationBase
from database.db_session import DBSession
from database.operations.process_number.process_number_base import CompletedProcessNumberOperationBase
from models.model import CompletedProcessNumber  ## sql db table 
from schemas.process_number import CompletedProcessNumberModel ## pydantic model 


class CompletedProcessNumberOperation(CompletedProcessNumberOperationBase, CRUDOperationBase[CompletedProcessNumber]):
    def __init__(self, db_session: DBSession):
        super().__init__(db_session)

    def get_model_class(self):
        return CompletedProcessNumberModel
    
    def convert_to_db_object(self, data: CompletedProcessNumberModel) -> CompletedProcessNumber:
        return CompletedProcessNumber(**data.dict())

    def create_process_number(self, process_number_data: CompletedProcessNumberModel) -> CompletedProcessNumber:
        return self.create(process_number_data)

    def get_process_number(self, process_number: int) -> CompletedProcessNumber:
        return self.get(process_number)

    def delete_process_number(self, process_number: int):
        return self.delete(process_number)

    def get_max_process_number(self) -> int:
        session = self.db_session.get_session()
        max_process_number = None
        try:
            max_process_number = session.query(func.max(CompletedProcessNumber.process_number)).scalar()
        finally:
            session.close()
        return max_process_number if max_process_number is not None else 0

    def get_next_process_number(self) -> int:
        max_process_number = self.get_max_process_number()
        return max_process_number + 1

    def complete_process(self) -> int:
        next_process_number = self.get_next_process_number()
        new_process = CompletedProcessNumberModel(process_number=next_process_number)
        self.create_process_number(new_process)
        return next_process_number
    