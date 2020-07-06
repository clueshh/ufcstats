import os
import configparser
from Database.models import Base, WeightClasses
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


class Database:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini'))
        self.db_uri = config['postgresql']['db_uri']
        self.engine = create_engine(self.db_uri, echo=False)

        Session = sessionmaker(bind=self.engine)
        self.session = Session()

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
