import scrapy
from string import ascii_lowercase

from Database import Database, current_database
from Database.models import Fighters
from ScrapeUFC.util import helpers, FighterParser

from sqlalchemy import update


class FightersSpider(scrapy.Spider):
    name = "ufcstats"
    start_urls = [f'http://www.ufcstats.com/statistics/fighters?char={c}&page=all' for c in ascii_lowercase]

    def parse(self, response):
        """
        Parses the fighters from the fighters page

        :param response:
        :return: None
        """

        table_rows = response.css("table.b-statistics__table tbody tr")
        for row in table_rows:
            fighter_url = row.css('td:nth-child(2) a.b-link.b-link_style_black::attr(href)').get()
            if fighter_url:
                # check if fighter has a belt
                belt_src = row.css('td:last-child img::attr(src)').get()
                belt = belt_src.split('/')[-1] == 'belt.png' if belt_src else False
                yield scrapy.Request(url=fighter_url, callback=self.parse_fighter_row, cb_kwargs=dict(belt=belt))

    @staticmethod
    def parse_fighter_row(response, belt):
        db = Database(current_database, True)

        fighter_id = helpers.get_url_id(response.request.url)
        fighter_info = FighterParser(db, response, fighter_id).serialize()
        if db.session.query(Fighters.id).filter_by(id=fighter_id).scalar() is None:
            # fighter doesn't exist in db so we create one
            fighter = Fighters(**fighter_info, belt=belt)
            db.session.add(fighter)
        else:
            # update fighter
            fighter_info.pop('id')
            # db.session.query(Fighters).filter(Fighters.id == fighter_id).update(**fighter_info, belt=belt)
            # Fighters.update().where(Fighters.id == fighter_id).values(**fighter_info, belt=belt)

            query = update(Fighters).where(Fighters.id == fighter_id).values(**fighter_info, belt=belt)
            db.session.execute(query)

        db.session.commit()
