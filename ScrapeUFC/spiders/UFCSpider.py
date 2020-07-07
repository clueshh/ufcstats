from datetime import datetime, date

import requests
import scrapy

from Database import Database
from Database.db_util.DatabaseINI import current_database
from Database.models import Events, Fights, Fighters, Rounds
from ScrapeUFC.util import helpers, FightParser, FightRoundParser, EventParser, FighterParser


class UFCSpider(scrapy.Spider):
    name = "ufcstats"
    start_urls = ['http://www.ufcstats.com/statistics/events/completed?page=all']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.overwrite_events = False
        self.overwrite_fighters = False
        self.overwrite_fights = False

    def parse(self, response):
        """
        Parses an the completed events page from the url:
            http://www.ufcstats.com/statistics/events/completed?page=all

        If the event has not finished or is already in the database it will be skipped

        :param response:
        :return: None
        """

        session = Database(current_database, True).get_session()

        event_urls = response.css("a.b-link::attr(href)").getall()
        dates_obj = [datetime.strptime(date_str.strip(), '%B %d, %Y').date()
                     for date_str in response.css('span.b-statistics__date::text').getall()]

        assert len(dates_obj) == len(event_urls), 'The number of dates should be the same as events'

        for event_url, date_obj in list(zip(event_urls, dates_obj))[0:2]:
            event_id = helpers.get_url_id(event_url)
            if date.today() <= date_obj:
                continue  # event has not finished
            # elif self.overwrite_events:
            #     yield scrapy.Request(url=event_url, callback=self.parse_events)
            elif session.query(Events.id).filter_by(id=event_id).scalar() is None:
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

        session = Database(current_database).get_session()

        event_id = helpers.get_url_id(response.request.url)
        event_info = EventParser(event_id, response, session).serialize()

        event = Events(**event_info)
        session.add(event)
        session.flush()

        # we cannot use yield here as we must ensure that the
        # fighter has been created before we create the fight

        # create fighters
        fighter_urls = response.css('a.b-link.b-link_style_black::attr(href)').getall()
        self.create_fighters(fighter_urls, session)
        session.flush()

        # now parse all fights on the card
        fight_urls = response.css("tbody.b-fight-details__table-body tr::attr(data-link)").getall()
        self.create_fights(fight_urls, session)
        session.commit()

    def create_fights(self, fight_urls, session):
        """
        Checks if a fight exists in the database and if not create it

        :param fight_urls: a list of urls to create fights from
        :param session: The database session
        :return:
        """

        fight_ids = [helpers.get_url_id(x) for x in fight_urls]

        for fight_id, fight_url in zip(fight_ids, fight_urls):
            if session.query(Fights.id).filter_by(id=fight_id).scalar() is None:
                # fight doesn't exist in db so we create one
                self.create_fight(fight_url, session)
                session.flush()

    @staticmethod
    def create_fight(url, session):
        """
        Parses a fight page from a url formatted:
            http://www.ufcstats.com/fight-details/<fightid>

        :param url: The url of the fight
        :param session: The database session
        :return: None
        """

        fight_id = helpers.get_url_id(url)
        response = scrapy.Selector(requests.get(url))

        fight_info = FightParser(fight_id, response, session).serialize()
        round_info = FightRoundParser(fight_id, response, session).serialize()

        fight = Fights(**fight_info)
        session.add(fight)
        session.flush()

        for round_ in round_info:
            session.add(Rounds(**round_))

    def create_fighters(self, fighter_urls, session):
        """
        Checks if a fighter exists in the database and if not create one

        :param fighter_urls: a list of urls to create
        :param session: The database session
        :return: None
        """

        fighter_ids = [helpers.get_url_id(x) for x in fighter_urls]

        for fighter_id, fighter_url in zip(fighter_ids, fighter_urls):
            if session.query(Fighters.id).filter_by(id=fighter_id).scalar() is None:
                # fighter doesn't exist in db so we create one
                self.create_fighter(fighter_url, session)
                session.flush()

    @staticmethod
    def create_fighter(url, session):
        """
         Creates a fighter from a url formatted:
            http://www.ufcstats.com/fighter-details/<fighterid>

        :param url: The url of the fighter
        :param session: The database session
        :return: None
        """

        fighter_id = helpers.get_url_id(url)
        response = scrapy.Selector(requests.get(url))
        fighter_info = FighterParser(fighter_id, response, session).serialize()

        fighter = Fighters(**fighter_info)
        session.add(fighter)
