from sqlalchemy import create_engine
from database.db_factory import DBFactory

class SQLiteFactory(DBFactory):
    def create_connection(self):
        engine = create_engine('sqlite:///sqlite_database.db')
        return engine
