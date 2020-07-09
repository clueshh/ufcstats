import os
import configparser


class DatabaseINI:
    def __init__(self):
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
        config = configparser.ConfigParser()
        config.read(path)

        self.section = config['postgresql']

    def get_db_uri(self, db_name):
        return f"postgres+psycopg2://{self.section['user']}:{self.section['password']}@{self.section['host']}/{db_name}"

    def get_value(self, key):
        return self.section[key]
