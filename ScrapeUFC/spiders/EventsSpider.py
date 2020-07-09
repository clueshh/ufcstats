from datetime import datetime, date

import scrapy
import requests

from Database import Database, current_database
from Database.models import Events, Fights, Fighters, Rounds, FightResult
from ScrapeUFC.util import helpers, FightParser, EventParser, FighterParser


class EventsSpider(scrapy.Spider):
    name = "ufcstats"
    start_urls = ['http://www.ufcstats.com/statistics/events/completed?page=all']

    def parse(self, response):
        """
        Parses the completed events pages from the url:
            http://www.ufcstats.com/statistics/events/completed?page=all

        If the event has not finished or is already in the database it will be skipped

        :param response:
        :return: None
        """

        db = Database(current_database, True)

        event_urls = response.css("a.b-link::attr(href)").getall()
        dates_obj = [datetime.strptime(date_str.strip(), '%B %d, %Y').date()
                     for date_str in response.css('span.b-statistics__date::text').getall()]

        assert len(dates_obj) == len(event_urls), 'The number of dates should be the same as events'

        self.logger.info(f'Scraping {len(event_urls)} events from: {response.url}')
        for event_url, date_obj in list(zip(event_urls, dates_obj)):
            event_id = helpers.get_url_id(event_url)
            if date.today() <= date_obj:
                continue  # event has not finished
            elif db.session.query(Events.id).filter_by(id=event_id).scalar() is None:
                # event does not exist in database
                yield scrapy.Request(url=event_url, callback=self.parse_events)

    def parse_events(self, response):
        """
        Parses an event page from a url formatted:
            http://www.ufcstats.com/event-details/<eventid>

        for each event we create all the fighters (if they don't already exist in the database)
        then we add all of the fights from the event to the database

        :param response:
        :return: None
        """

        db = Database(current_database)

        event_id = helpers.get_url_id(response.request.url)
        event_info = EventParser(db, response, event_id).serialize()

        event = Events(**event_info)
        db.session.add(event)
        db.session.flush()

        # we cannot use yield here as we must ensure that the
        # fighter has been created before we create the fight

        # create fighters
        fighter_urls = response.css('a.b-link.b-link_style_black::attr(href)').getall()
        self.create_fighters(db, fighter_urls)
        db.session.flush()

        # now parse all fights on the card
        fight_urls = response.css("tbody.b-fight-details__table-body tr::attr(data-link)").getall()
        self.create_fights(db, fight_urls)
        db.session.commit()

    def create_fights(self, db, fight_urls):
        """
        Checks if a fight exists in the database and if not create it

        :param fight_urls: a list of urls to create fights from
        :param db: The database session
        :return:
        """

        fight_ids = [helpers.get_url_id(x) for x in fight_urls]

        for card_position, (fight_id, fight_url) in enumerate(zip(fight_ids, fight_urls), 1):
            if db.session.query(Fights.id).filter_by(id=fight_id).scalar() is None:
                # fight doesn't exist in db so we create one
                self.create_fight(db, fight_url, card_position)
                db.session.flush()

    @staticmethod
    def create_fight(db, url, card_position):
        """
        Parses a fight page from a url formatted:
            http://www.ufcstats.com/fight-details/<fightid>

        :param card_position: The position of the fight on the card
        :param db:
        :param url: The url of the fight
        :return: None
        """

        fight_id = helpers.get_url_id(url)
        response = scrapy.Selector(requests.get(url))

        fight_info = FightParser(db, response, fight_id).serialize()

        fight = Fights(**fight_info.get('fight_table'), card_position=card_position)
        db.session.add(fight)
        db.session.flush()

        for round_ in fight_info.get('rounds_table'):
            db.session.add(Rounds(**round_))

        for fighter in fight_info.get('result_table'):
            db.session.add(FightResult(**fighter))

    def create_fighters(self, db, fighter_urls):
        """
        Checks if a fighter exists in the database and if not create one

        :param db:
        :param fighter_urls: a list of urls to create
        :return: None
        """

        fighter_ids = [helpers.get_url_id(x) for x in fighter_urls]

        for fighter_id, fighter_url in zip(fighter_ids, fighter_urls):
            if db.session.query(Fighters.id).filter_by(id=fighter_id).scalar() is None:
                # fighter doesn't exist in db so we create one
                self.create_fighter(db, fighter_url)
                db.session.flush()

    @staticmethod
    def create_fighter(db, url):
        """
         Creates a fighter from a url formatted:
            http://www.ufcstats.com/fighter-details/<fighterid>

        :param db:
        :param str url: The url of the fighter
        :return: None
        """

        fighter_id = helpers.get_url_id(url)
        response = scrapy.Selector(requests.get(url))
        print(response, fighter_id)
        fighter_info = FighterParser(db, response, fighter_id).serialize()

        fighter = Fighters(**fighter_info)
        db.session.add(fighter)
