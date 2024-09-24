from abc import ABC, abstractmethod
from database.db_session import DBSession
from models.model import CompletedProcessNumber  ## sql db table 
from schemas.process_number import CompletedProcessNumberModel ## pydantic model 

class CompletedProcessNumberOperationBase(ABC):
    def __init__(self, db_session: DBSession):
        self.db_session = db_session

    @abstractmethod
    def create_process_number(self, process_number_data: CompletedProcessNumberModel):
        pass

    @abstractmethod
    def convert_to_db_object(self, data: CompletedProcessNumberModel) -> CompletedProcessNumber:
        pass

    @abstractmethod
    def get_process_number(self, process_number: int) -> CompletedProcessNumber:
        pass

    @abstractmethod
    def delete_process_number(self, process_number: int):
        pass

    @abstractmethod
    def get_max_process_number(self) -> int:
        pass

    @abstractmethod 
    def complete_process(self) -> int:
        pass 