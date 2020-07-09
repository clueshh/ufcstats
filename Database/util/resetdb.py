from Database import Database, current_database

if __name__ == '__main__':
    if current_database != 'ufcstats':
        Database(current_database, False).reset_db()
