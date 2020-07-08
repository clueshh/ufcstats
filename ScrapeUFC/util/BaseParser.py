
class BaseParser:
    def __init__(self, db, response):
        self.response = response
        self.db = db
        self.domain = 'http://www.ufcstats.com'
