from abc import ABC, abstractmethod

class DBFactory(ABC):
    @abstractmethod
    def create_connection(self):
        pass
