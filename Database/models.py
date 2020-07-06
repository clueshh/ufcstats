from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Date, CHAR, Time

Base = declarative_base()


class Events(Base):
    __tablename__ = "events"

    id = Column(String(16), primary_key=True, nullable=False)
    location_id = Column(Integer, ForeignKey('location.id'))
    name = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    attendance = Column(Integer, nullable=True)

    relationship("Location", foreign_keys=location_id)

    def __str__(self) -> str:
        return f'<Event id: {self.id},' \
               f' location_id: {self.location_id},' \
               f' name: {self.name},' \
               f' date: {self.date},' \
               f' attendance: {self.attendance}>'


class Location(Base):
    __tablename__ = "location"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    city = Column(String, nullable=False)
    region = Column(String, nullable=True)
    country = Column(String, nullable=False)


class Fights(Base):
    __tablename__ = "fights"

    id = Column(String(16), primary_key=True, nullable=False)
    fighter_a_id = Column(String(16), ForeignKey('fighters.id'), nullable=False)
    fighter_b_id = Column(String(16), ForeignKey('fighters.id'), nullable=False)
    winner = Column(String(2), nullable=False)  # can be either 'A', 'B', 'D' (draw) or 'NC' (No Contest)
    event_id = Column(String(16), ForeignKey('events.id'), nullable=False)
    gender = Column(CHAR, nullable=False)  # 'M' or 'F'

    weight_class_id = Column(Integer, ForeignKey('weightclasses.id'), nullable=True)

    method = Column(String(128), nullable=False)
    round = Column(Integer, nullable=False)
    time = Column(Time, nullable=False)
    rounds = Column(Integer, nullable=False)
    time_format = Column(String(50), nullable=False)
    referee = Column(String(64), nullable=False)
    details = Column(String(256), nullable=False)

    title_bout = Column(Boolean, nullable=False)
    # bonus's
    performance_bonus = Column(Boolean, nullable=False)
    fotn_bonus = Column(Boolean, nullable=False)
    sub_bonus = Column(Boolean, nullable=False)
    ko_bonus = Column(Boolean, nullable=False)

    relationship("Fighters", foreign_keys=fighter_a_id)
    relationship("Fighters", foreign_keys=fighter_b_id)
    relationship("Events", foreign_keys=event_id)
    relationship("WeightClasses", foreign_keys=weight_class_id)


class Rounds(Base):
    __tablename__ = "rounds"

    fight_id = Column(String(16), ForeignKey('fights.id'), nullable=False, primary_key=True)
    fighter_id = Column(String(16), ForeignKey('fighters.id'), nullable=False, primary_key=True)
    round = Column(Integer, nullable=False, primary_key=True)

    kd = Column(Integer, nullable=False)                    # knockdowns
    sig_str = Column(Integer, nullable=False)               # significant strikes
    sig_str_attempts = Column(Integer, nullable=False)      # significant strike attempts
    total_str = Column(Integer, nullable=False)             # total strikes
    total_str_attempts = Column(Integer, nullable=False)    # total strike attempts
    td = Column(Integer, nullable=False)                    # take downs
    td_attempts = Column(Integer, nullable=False)           # take down attempts
    sub_att = Column(Integer, nullable=False)               # submission attempts
    pass_ = Column(Integer, nullable=False)                 # ?
    rev = Column(Integer, nullable=False)                   # ?

    # significant strike location
    head = Column(Integer, nullable=False)
    head_attempts = Column(Integer, nullable=False)
    body = Column(Integer, nullable=False)
    body_attempts = Column(Integer, nullable=False)
    leg = Column(Integer, nullable=False)
    leg_attempts = Column(Integer, nullable=False)
    distance = Column(Integer, nullable=False)
    distance_attempts = Column(Integer, nullable=False)
    clinch = Column(Integer, nullable=False)
    clinch_attempts = Column(Integer, nullable=False)
    ground = Column(Integer, nullable=False)
    ground_attempts = Column(Integer, nullable=False)

    relationship("Fights", foreign_keys=fight_id)
    relationship("Fighters", foreign_keys=fighter_id)


class Fighters(Base):
    __tablename__ = "fighters"

    id = Column(String(16), primary_key=True, nullable=False)
    first_name = Column(String(64), nullable=False)
    last_name = Column(String(64), nullable=False)
    nickname = Column(String(64), nullable=True)
    height = Column(Float(16), nullable=True)
    weight = Column(Integer, nullable=True)
    reach = Column(Integer, nullable=True)
    stance = Column(String(20), nullable=True)
    dob = Column(Date, nullable=True)

    wins = Column(Integer, nullable=False)
    losses = Column(Integer, nullable=False)
    draws = Column(Integer, nullable=False)
    nc = Column(Integer, nullable=False)


class WeightClasses(Base):
    __tablename__ = "weightclasses"

    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    name = Column(String(50), nullable=False)
    weight = Column(Integer, nullable=False)
