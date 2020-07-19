from sqlalchemy.dialects import postgresql as pg_sql
from sqlalchemy import func, desc, cast, and_, distinct, FLOAT

from Database.models import Fighters, FightResult, Fights, Rounds


class Career:
    def __init__(self, db):
        self.db = db

    def fastest_finish(self):
        # http://statleaders.ufc.com/fight/#ShortestFight-group
        raise NotImplementedError

    def fastest_ko_tko(self):
        # http://statleaders.ufc.com/fight/#ShortestKOTKO-group
        raise NotImplementedError

    def fastest_submission(self):
        # http://statleaders.ufc.com/fight/#ShortestSubmission-group
        raise NotImplementedError

    def latest_finish(self):
        # http://statleaders.ufc.com/fight/#LatestFinish-group
        raise NotImplementedError

    def latest_ko_tko(self):
        # http://statleaders.ufc.com/fight/#LatestKOTKO-group
        raise NotImplementedError

    def latest_submission(self):
        # http://statleaders.ufc.com/fight/#LatestSubmission-group
        raise NotImplementedError

    def knockdowns_landed(self):
        # http://statleaders.ufc.com/fight/#KnockDowns-group
        # Min 3 knockdowns
        raise NotImplementedError

    def striking_differential(self):
        # http://statleaders.ufc.com/fight/#PlusMinus-group
        raise NotImplementedError

    def largest_comeback_finish(self):
        # http://statleaders.ufc.com/fight/#BiggestStrikingComeback-group
        raise NotImplementedError

    def sig_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#SigStrikesLanded-group
        raise NotImplementedError

    def sig_strikes_attempted(self):
        # http://statleaders.ufc.com/fight/#SigStrikesAttempted-group
        raise NotImplementedError

    def sig_strike_accuracy(self):
        # http://statleaders.ufc.com/fight/#SigStrikesAccuracy-group
        raise NotImplementedError

    def distance_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#SigDistanceStrikesLanded-group
        raise NotImplementedError

    def clinch_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#SigClinchStrikesLanded-group
        raise NotImplementedError

    def ground_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#SigGroundStrikesLanded-group
        raise NotImplementedError

    def head_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#SigHeadStrikesLanded-group
        raise NotImplementedError

    def body_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#SigBodyStrikesLanded-group
        raise NotImplementedError

    def leg_kicks_landed(self):
        # http://statleaders.ufc.com/fight/#LegKicksLanded-group
        raise NotImplementedError

    def total_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#TotStrikesLanded-group
        raise NotImplementedError

    def total_strikes_attempted(self):
        # http://statleaders.ufc.com/fight/#TotStrikesAttempted-group
        raise NotImplementedError

    def total_clinch_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#TotClinchStrikesLanded-group
        raise NotImplementedError

    def total_ground_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#TotGroundStrikesLanded-group
        raise NotImplementedError

    def total_head_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#TotHeadStrikesLanded-group
        raise NotImplementedError

    def total_body_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#TotBodyStrikesLanded-group
        raise NotImplementedError

    def total_leg_strikes_landed(self):
        # http://statleaders.ufc.com/fight/#TotLegStrikesLanded-group
        raise NotImplementedError

    def take_downs_landed(self):
        # http://statleaders.ufc.com/fight/#TakedownsLanded-group
        # Minimum 5
        raise NotImplementedError

    def take_downs_attempted(self):
        # http://statleaders.ufc.com/fight/#TakedownsAttempted-group
        # Minimum 10
        raise NotImplementedError

    def take_down_accuracy(self):
        # http://statleaders.ufc.com/fight/#TakedownAccuracy-group
        # Minimum 10 take down attempts
        raise NotImplementedError

    def submission_attempts(self):
        # http://statleaders.ufc.com/fight/#SubmissionAttempts-group
        # Minimum 3
        raise NotImplementedError

