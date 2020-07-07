from Database import Database, current_database

if __name__ == '__main__':
    Database(current_database, False).drop_db()
