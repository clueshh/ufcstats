from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

from Database.db_util.DatabaseINI import DatabaseINI
from Database.models import Base, WeightClasses


class Database:
    def __init__(self, db_name, auto_create=False):
        self.db_name = db_name
        self.ini = DatabaseINI()
        self.db_uri = f'{self.ini.get_db_uri()}/{self.db_name}'

        self.engine = create_engine(self.db_uri, echo=False)
        self.base_engine = create_engine(f"postgres://postgres:{self.ini.get_value('password')}@/postgres")

        try:
            self.engine.connect()
        except OperationalError as e:
            if auto_create:
                self.create_db()
            else:
                raise e

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def drop_db(self):
        conn = self.base_engine.connect()
        conn.execute(f"SELECT pg_terminate_backend(pg_stat_activity.pid) "
                     f"FROM pg_stat_activity "
                     f"WHERE datname = '{self.db_name}' "
                     f"AND pid <> pg_backend_pid();")

        conn.execution_options(isolation_level="AUTOCOMMIT")
        conn.execute(f"DROP DATABASE {self.db_name}")
        conn.close()

        self.session = self.engine = None

    def create_db(self):
        conn = self.base_engine.connect()
        conn.execute("COMMIT")
        conn.execute(f"CREATE DATABASE {self.db_name}")
        conn.close()

    def drop_all(self):
        Base.metadata.drop_all(bind=self.engine)

    def create_all(self):
        Base.metadata.create_all(self.engine)

    def reset_db(self):
        # Drop and Create All Tables
        self.drop_all()
        self.create_all()

        weight_classes = {'Strawweight': 115,
                          'Flyweight': 125,
                          'Bantamweight': 135,
                          'Featherweight': 145,
                          'Lightweight': 155,
                          'Super lightweight': 165,
                          'Welterweight': 170,
                          'Super welterweight': 175,
                          'Middleweight': 185,
                          'Super middleweight': 195,
                          'Light heavyweight': 205,
                          'Cruiserweight': 225,
                          'Heavyweight': 265}

        for name, weight in weight_classes.items():
            self.session.add(WeightClasses(name=name, weight=weight))

        self.session.commit()

    def get_engine(self):
        return self.engine

    def get_session(self):
        return self.session
