from Database import Database, current_database
from Database.Queries.StatsLeaders.Career import Career


class StatsLeaders:
    """
    A class to get the stats found at:
        http://statleaders.ufc.com/
    """

    def __init__(self):
        self.db = Database(current_database)
        self.career = Career(self.db)
        self.fight = None
        self.fight_comb = None
        self.round = None
        self.round_comb = None
        self.event = None
