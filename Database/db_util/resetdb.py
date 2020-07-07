from Database import Database
from Database.db_util.DatabaseINI import current_database

if __name__ == '__main__':
    Database(current_database).reset_db()
