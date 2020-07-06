from datetime import datetime

from sqlalchemy import func

from Database.models import WeightClasses
from ScrapeUFC.util import helpers, BaseFightParser


class FightParser(BaseFightParser):
    def __init__(self, fight_id, response, session):
        super().__init__(fight_id, response, session)

        self.event_id = self.get_event_id()
        self.winner = self.get_fight_winner()

        self.details = self.response.css('div.b-fight-details__fight')
        # from details pane
        self.title_bout, \
            self.fotn_bonus, \
            self.performance_bonus, \
            self.sub_bonus, \
            self.ko_bonus = self.get_title_bonus()

        self.details_ = self.get_details()
        self.method = self.get_method()
        self.round = self.get_round()
        self.time = self.get_time()
        self.time_format = self.get_time_format()
        self.rounds = self.get_rounds()
        self.referee = self.get_referee()

        self.gender = self.get_gender()
        self.weight_class_id = self.get_weight_class_id()

    def serialize(self):
        return dict(id=self.fight_id,
                    fighter_a_id=self.fighter_a_id,
                    fighter_b_id=self.fighter_b_id,
                    event_id=self.event_id,
                    weight_class_id=self.weight_class_id,
                    winner=self.winner,
                    gender=self.gender,
                    method=self.method,
                    round=self.round,
                    time=self.time,
                    rounds=self.rounds,
                    referee=self.referee,
                    details=self.details_,
                    title_bout=self.title_bout,
                    fotn_bonus=self.fotn_bonus,
                    performance_bonus=self.performance_bonus,
                    sub_bonus=self.sub_bonus,
                    ko_bonus=self.ko_bonus,
                    time_format=self.time_format)

    def get_fight_winner(self):
        result_0 = self.fighters[0].css('i.b-fight-details__person-status::text').get().strip()
        result_1 = self.fighters[1].css('i.b-fight-details__person-status::text').get().strip()

        if result_0 == 'W' and result_1 == 'L':
            return 'A'
        elif result_0 == 'L' and result_1 == 'W':
            return 'B'
        elif result_0 == 'D' and result_1 == 'D':
            return 'D'
        elif result_0 == 'NC' and result_1 == 'NC':
            return 'NC'
        else:
            raise ValueError('Fight result ambiguous')

    def get_event_id(self):
        return helpers.get_url_id(self.response.css('h2.b-content__title a::attr(href)').get())

    def get_weight_class_id(self):
        title = self.details.css('i.b-fight-details__fight-title::text').extract()[-1] \
            .strip().lower().replace(' ', '-')

        result = self.session.query(WeightClasses.id,
                                    func.replace(func.lower(WeightClasses.name), ' ', '-').label('name')).all()
        for row in result:
            if row.name in title:
                return row.id

        return None

    def get_gender(self):
        fight_title = self.details.css('i.b-fight-details__fight-title::text').extract()[-1].strip().lower()
        return 'F' if 'women' in fight_title else 'M'

    def get_method(self):
        return self.details.xpath("//*[contains(text(), 'Method:')]/..").css('i>i:nth-child(2)::text').get().strip()

    def get_round(self):
        return int(self.details.xpath("//*[contains(text(), 'Round:')]/..").css('*::text').extract()[-1].strip())

    def get_time(self):
        t = self.details.xpath("//*[contains(text(), 'Time:')]/..").css('*::text').extract()[-1].strip()
        return datetime.strptime(t, '%M:%S').time()

    def get_rounds(self):
        ext = self.details.xpath("//*[contains(text(), 'Time format:')]/..").css('*::text').extract()[-1].strip()
        if self.time_format == 'No Time Limit':
            return -1
        else:
            try:
                return int(self.time_format.split(' ')[0])
            except ValueError:
                raise ValueError(f'No valid parser for \'{ext}\'')

    def get_time_format(self):
        return self.details.xpath("//*[contains(text(), 'Time format:')]/..").css('*::text').extract()[-1].strip()

    def get_referee(self):
        return self.details.xpath("//*[contains(text(), 'Referee:')]/..").css('span::text').get().strip()

    def get_details(self):
        text = self.details.xpath("//*[contains(text(), 'Details:')]/../..").css('*::text').extract()
        return ''.join([x.strip() for x in text]).split(':')[-1]

    def get_title_bonus(self):
        images = self.details.css('i.b-fight-details__fight-title img')

        perf = belt = fight = sub = ko = False

        for image in images:
            text = image.css('img::attr(src)').get().split('/')[-1]
            if text == 'perf.png':
                perf = True
            elif text == 'belt.png':
                belt = True
            elif text == 'fight.png':
                fight = True
            elif text == 'sub.png':
                sub = True
            elif text == 'ko.png':
                ko = True
            else:
                raise ValueError(f'Unknown image {text}')

        return belt, perf, fight, sub, ko
