from sqlalchemy import create_engine
from database.db_factory import DBFactory

class MySQLFactory(DBFactory):
    def create_connection(self):
        # Replace the parameters below with your MySQL connection details
        engine = create_engine('mysql://user:password@localhost/database_name')
        return engine
