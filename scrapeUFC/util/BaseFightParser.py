from Database.models import Fighters
from scrapeUFC.util import helpers, BaseParser


class BaseFightParser(BaseParser):
    def __init__(self, fight_id, response, session):
        super().__init__(response, session)

        self.fight_id = fight_id
        self.base_url = 'http://www.ufcstats.com/fight-details/'

        self.fighters = self.response.css('div.b-fight-details__person')
        assert len(self.fighters) == 2, 'Fight must have 2 fighters'

        self.fighter_a_id, self.fighter_b_id = self.get_fighter_ids()

    def get_fighter_ids(self):
        fighter_ids = []
        for fighter in self.fighters:
            url = fighter.css('a::attr(href)').get()
            if url:
                fighter_ids.append(helpers.get_url_id(url))
            else:
                first_name, last_name = helpers.split_name(
                    fighter.css(
                        'span.b-link.b-fight-details__person-link::text'
                    ).get())

                fighter_id = self.session.query(Fighters.id). \
                    filter_by(first_name=first_name, last_name=last_name).first()

                assert fighter_id, f'The fighter {first_name, last_name} does not exist in the database.'

                fighter_ids.append(fighter_id[0])

        return fighter_ids
