from database.mysql.mysql_connection import MySQLFactory
from database.sqlite.sqlite_connection import SQLiteFactory

class DatabaseFactory:
    @staticmethod
    def create_connection(db_type: str):
        if db_type == 'sqlite':
            return SQLiteFactory().create_connection()
        elif db_type == 'mysql':
            return MySQLFactory().create_connection()
        else:
            raise ValueError("Unsupported database type")
