
class BaseParser:
    def __init__(self, response, db):
        self.response = response
        self.db = db
        self.domain = 'http://www.ufcstats.com'
