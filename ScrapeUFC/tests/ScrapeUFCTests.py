import requests
import scrapy

from Database import Database, current_database
from ScrapeUFC.util import FightParser, FightRoundParser, FighterParser, EventParser, helpers


class ScrapeUFCTests:
    def __init__(self, event_urls=None, fight_urls=None, fighter_urls=None):
        if event_urls:
            self.event_urls = event_urls
            self.event_ids = [helpers.get_url_id(x) for x in self.event_urls]

        if fight_urls:
            self.fight_urls = fight_urls
            self.fight_ids = [helpers.get_url_id(x) for x in self.fight_urls]

        if fighter_urls:
            self.fighter_urls = fighter_urls
            self.fighter_ids = [helpers.get_url_id(x) for x in self.fighter_urls]

        self.session = Database(current_database, True).get_session()

    def test_factory(self, urls, ids, func):
        responses = [scrapy.Selector(requests.get(url)) for url in urls]
        for idx, response in zip(ids, responses):
            parser = func(idx, response, self.session)
            print(parser.serialize())

    def test_fight_parser(self):
        if self.fight_urls:
            self.test_factory(self.fight_urls, self.fight_ids, FightParser)

    def test_round_parser(self):
        if self.fight_urls:
            self.test_factory(self.fight_urls, self.fight_ids, FightRoundParser)

    def test_fighter_parser(self):
        if self.fighter_urls:
            self.test_factory(self.fighter_urls, self.fighter_ids, FighterParser)

    def test_event_parser(self):
        if self.event_urls:
            self.test_factory(self.event_urls, self.event_ids, EventParser)


if __name__ == '__main__':
    fights = ['http://www.ufcstats.com/fight-details/67ed3ad521ef619c',
              'http://www.ufcstats.com/fight-details/1b8d366ac0f110f3',
              'http://www.ufcstats.com/fight-details/d395828f5cb045a5',
              'http://www.ufcstats.com/fight-details/dc38c78358e053c3',
              'http://www.ufcstats.com/fight-details/8539c4b795d33a92']

    events = ['http://www.ufcstats.com/event-details/c32eab6c2119e989',
              'http://www.ufcstats.com/event-details/4c12aa7ca246e7a4',
              'http://www.ufcstats.com/event-details/5f8e00c27b7e7410']

    fighters = ['http://www.ufcstats.com/fighter-details/ebef46976554f975',
                'http://www.ufcstats.com/fighter-details/5f3805dda9661cba',
                'http://www.ufcstats.com/fighter-details/029eaff01e6bb8f0']

    tests = ScrapeUFCTests(fight_urls=fights, event_urls=events, fighter_urls=fighters)
    tests.test_fight_parser()
    tests.test_round_parser()
    tests.test_fighter_parser()
    tests.test_event_parser()
