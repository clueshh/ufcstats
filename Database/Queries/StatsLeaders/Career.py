from sqlalchemy.dialects import postgresql as pg_sql
from sqlalchemy import func, desc, cast, and_, distinct, FLOAT

from Database.models import Fighters, FightResult, Fights, Rounds


class Career:
    def __init__(self, db):
        self.db = db

    def __base_fighter_query(self, label=None):
        return self.db.session.query(Fighters.full_name,
                                     func.count(Fighters.id).label(label if label else 'count')) \
            .join(FightResult, FightResult.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .order_by(func.count(FightResult.fighter_id).desc())

    def __base_fighter_fights_query(self, label=None):
        return self.__base_fighter_query(label).join(Fights, Fights.id == FightResult.fight_id)

    def __fighter_fights_wins(self, label=None):
        return self.__base_fighter_fights_query(label).filter(FightResult.result == 'W')

    def count_ufc_fights(self):
        # http://statleaders.ufc.com/career/#TotalFights-group
        return self.__base_fighter_query('Total Fights')

    def count_ufc_wins(self, label=None):
        return self.__base_fighter_query(label if label else 'Total Wins').filter(FightResult.result == 'W')

    def count_ufc_losses(self, label=None):
        return self.__base_fighter_query(label if label else 'Total Losses').filter(FightResult.result == 'L')

    def count_ufc_draws(self, label=None):
        return self.__base_fighter_query(label if label else 'Total Draws').filter(FightResult.result == 'D')

    def count_ufc_nc(self, label=None):
        return self.__base_fighter_query(label if label else 'Total No Contest').filter(FightResult.result == 'NC')

    def finishes(self):
        # http://statleaders.ufc.com/career/#Finishes-group
        return self.__fighter_fights_wins('finishes').filter(Fights.method.op('~*')('.*KO.*|.*submission.*'))

    def ko_tko_wins(self):
        # http://statleaders.ufc.com/career/#KOTKOWins-group
        return self.__fighter_fights_wins('ko/tko').filter(Fights.method.op('~*')('.*KO.*'))

    def submission_wins(self):
        # http://statleaders.ufc.com/career/#SubmissionWins-group
        return self.__fighter_fights_wins('submissions').filter(Fights.method.op('~*')('.*submission.*'))

    def decision_wins(self):
        # http://statleaders.ufc.com/career/#DecisionWins-group
        return self.__fighter_fights_wins('decisions').filter(Fights.method.op('~*')('.*decision.*'))

    def win_streak(self):
        # http://statleaders.ufc.com/career/#WinStreak-group
        raise NotImplementedError

    def title_fight_wins(self):
        # http://statleaders.ufc.com/career/#TitleFightWins-group
        return self.__fighter_fights_wins().filter(Fights.title_bout == 'True')

    def fight_bonuses(self):
        # http://statleaders.ufc.com/career/#TotalAwards-group
        raise NotImplementedError

    def avg_fight_time(self):
        # http://statleaders.ufc.com/career/#AvgFightTimeShort-group
        # http://statleaders.ufc.com/career/#AvgFightTimeLong-group
        # Min 5 fights

        subquery1 = self.db.session.query(Fighters.id,
                                          func.count(FightResult.fighter_id).label('num_fights')) \
            .join(Fighters, Fighters.id == FightResult.fighter_id) \
            .group_by(Fighters.id) \
            .having(func.count('num_fights') >= 5) \
            .subquery()

        subquery2 = self.db.session.query(Fighters.id,
                                          func.sum(Rounds.actual_round_length).label('total_round_length')) \
            .join(Rounds, Rounds.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .subquery()

        return self.db.session.query(Fighters.full_name,
                                     (
                                             cast('1 sec', pg_sql.INTERVAL) *
                                             (func.extract('epoch',
                                                           subquery2.c.total_round_length
                                                           ) / subquery1.c.num_fights
                                              )
                                     ).label('avg_fight_time')) \
            .join(subquery1, subquery1.c.id == Fighters.id) \
            .join(subquery2, subquery2.c.id == subquery1.c.id) \
            .order_by('avg_fight_time')

    def __base_rounds_query(self, label, agg_func, order=desc):
        return self.db.session.query(Fighters.full_name, agg_func.label(label)) \
            .join(Rounds, Rounds.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .order_by(order(label))

    def total_fight_time(self):
        # http://statleaders.ufc.com/career/#TotFightTime-group
        return self.__base_rounds_query('total_time', func.sum(Rounds.actual_round_length))

    def knockdowns_landed(self):
        # http://statleaders.ufc.com/career/#KnockDowns-group
        return self.__base_rounds_query('kd', func.sum(Rounds.kd))

    def avg_kd_per_15m(self):
        # http://statleaders.ufc.com/career/#KnockdownAverage-group
        # Min 5 fights

        return self.db.session.query(Fighters.full_name,
                                     (
                                             func.extract('epoch',
                                                          (cast('15 minutes', pg_sql.INTERVAL)) * func.sum(Rounds.kd)) /
                                             func.extract('epoch',
                                                          func.sum(Rounds.actual_round_length))
                                     ).label('avg_kd_per_15m'),
                                     ) \
            .join(Rounds, Rounds.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .having(and_(func.sum(Rounds.kd) > 0,
                         func.count(distinct(Rounds.fight_id)) >= 5)) \
            .order_by(desc('avg_kd_per_15m'))

    def sig_str_landed(self):
        # http://statleaders.ufc.com/career/#SigStrikesLanded-group
        return self.__base_rounds_query('sig_str', func.sum(Rounds.sig_str))

    def sig_str_accuracy(self):
        # http://statleaders.ufc.com/career/#SigStrikesAccuracy-group
        # Min 5 fights & 350 significant strike attempts

        return self.db.session.query(Fighters.full_name,
                                     ((cast(func.sum(Rounds.sig_str), FLOAT) / func.sum(
                                         Rounds.sig_str_attempts)) * 100).label('sig_str_accuracy')) \
            .join(Rounds, Rounds.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .having(and_(func.sum(Rounds.sig_str_attempts) >= 350,
                         func.count(distinct(Rounds.fight_id)) >= 5)) \
            .order_by(desc('sig_str_accuracy'))

    def sig_str_per_min(self):
        # http://statleaders.ufc.com/career/#SLpM-group
        # Min 5 fights

        return self.db.session.query(Fighters.full_name,
                                     (func.extract('epoch',
                                                   (cast('1 minutes', pg_sql.INTERVAL)) * func.sum(Rounds.sig_str)) /
                                      func.extract('epoch',
                                                   func.sum(Rounds.actual_round_length))).label('sig_str_per_min')) \
            .join(Rounds, Rounds.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .having(func.count(distinct(Rounds.fight_id)) >= 5) \
            .order_by(desc('sig_str_per_min'))

    def striking_differential(self):
        # http://statleaders.ufc.com/career/#PlusMinus-group
        # Min 5 fights
        raise NotImplementedError

    def sig_str_defence(self):
        # http://statleaders.ufc.com/career/#SigStrikingDefense-group
        # Min 5 fights & 350 significant strike attempts by opponents
        raise NotImplementedError

    def str_absorbed_per_min(self):
        # http://statleaders.ufc.com/career/#SApM-group
        # Min 5 fights
        raise NotImplementedError

    def total_str_landed(self):
        # http://statleaders.ufc.com/career/#TotStrikesLanded-group
        return self.__base_rounds_query('total_str', func.sum(Rounds.total_str))

    def take_downs_landed(self):
        # http://statleaders.ufc.com/career/#TakedownsLanded-group
        return self.__base_rounds_query('take_downs', func.sum(Rounds.td))

    def take_down_accuracy(self):
        # http://statleaders.ufc.com/career/#TakedownAccuracy-group
        # Min 5 fights & 20 take down attempts

        return self.db.session.query(Fighters.full_name,
                                     ((cast(func.sum(Rounds.td), FLOAT) / func.sum(
                                         Rounds.td_attempts)) * 100).label('take_down_accuracy')) \
            .join(Rounds, Rounds.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .having(and_(func.sum(Rounds.td_attempts) >= 20,
                         func.count(distinct(Rounds.fight_id)) >= 5)) \
            .order_by(desc('take_down_accuracy'))

    def take_down_defence(self):
        # http://statleaders.ufc.com/career/#TakedownDefense-group
        # Min 5 fights and 20 take down attempts by opponent
        raise NotImplementedError

    def submission_attempts(self):
        # http://statleaders.ufc.com/career/#SubmissionAttempts-group
        return self.__base_rounds_query('sub_att', func.sum(Rounds.sub_att))

    def submission_avg_per_15m(self):
        # http://statleaders.ufc.com/career/#SubmissionAverage-group
        # Min 5 fights

        return self.db.session.query(Fighters.full_name,
                                     (
                                             func.extract('epoch',
                                                          (cast('15 minutes', pg_sql.INTERVAL)) * func.sum(Rounds.kd)) /
                                             func.extract('epoch',
                                                          func.sum(Rounds.actual_round_length))
                                     ).label('avg_kd_per_15m'),
                                     ) \
            .join(Rounds, Rounds.fighter_id == Fighters.id) \
            .group_by(Fighters.id) \
            .having(and_(func.sum(Rounds.kd) > 0,
                         func.count(distinct(Rounds.fight_id)) >= 5)) \
            .order_by(desc('avg_kd_per_15m'))
