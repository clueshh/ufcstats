
class BaseParser:
    def __init__(self, response, session):
        self.response = response
        self.session = session
        self.domain = 'http://www.ufcstats.com'
