from sqlalchemy.orm import sessionmaker
from database.get_db import DatabaseFactory 

class DBSession:
    def __init__(self, db_type: str):
        self._connection = DatabaseFactory.create_connection(db_type)
        self.Session = sessionmaker(bind=self._connection)

    @property
    def connection(self):
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value
        # Re-bind session maker to the new connection
        self.Session.configure(bind=self._connection)

    def get_session(self):
        # Create and return a session
        return self.Session()
    
    def close_connection(self):
        # Close the database connection
        self._connection.close()
