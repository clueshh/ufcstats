import re
from datetime import datetime

from ScrapeUFC.util import BaseParser, helpers


class FighterParser(BaseParser):
    def __init__(self, fighter_id, response, session):
        super().__init__(response, session)

        self.fighter_id = fighter_id
        self.base_url = self.domain + '/fighter-details'

        self.height, self.weight, self.reach, self.stance, self.dob = self.get_attributes()
        self.wins, self.losses, self.draws, self.nc = self.get_record()

        self.first_name, self.last_name = helpers.split_name(response.css('h2.b-content__title span::text').get())
        nickname = response.css('.b-content__Nickname::text').get().strip()
        self.nickname = None if len(nickname) == 0 else nickname

    def serialize(self):
        return dict(id=self.fighter_id,
                    first_name=self.first_name,
                    last_name=self.last_name,
                    nickname=self.nickname,
                    height=self.height,
                    weight=self.weight,
                    reach=self.reach,
                    stance=self.stance,
                    dob=self.dob,
                    wins=self.wins,
                    losses=self.losses,
                    draws=self.draws,
                    nc=self.nc)

    def get_record(self):
        record = self.response.css('span.b-content__title-record::text').get().strip().split('Record: ')[-1]
        record_spl = record.split('-')
        assert len(record_spl) == 3
        if re.match(r'\d*-\d*-\d* [(]\d NC[)]', record):
            assert 'NC' in record_spl[-1]
            nc = re.search(r"\d* NC", record_spl[-1]).group(0).split(' ')[0]

            record_spl[-1] = record_spl[-1].split(' ')[0]
            record_spl.append(nc)

            wins, losses, draws, nc = [int(x) for x in record_spl]
        elif re.match(r'\d*-\d*-\d*', record):
            nc = 0
            wins, losses, draws = [int(x) for x in record_spl]
        else:
            raise ValueError(f"Invalid Record '{record}'")

        return wins, losses, draws, nc

    def get_attributes(self):
        attr = self.response.css('ul.b-list__box-list li')

        height = weight = reach = stance = dob = None
        for li in attr:
            text = li.css('*::text').extract()[-1].strip()
            if text in ['--', '']:
                continue
            elif li.re(helpers.re_compile('height:')):
                ft, inches = text.split(' ')
                ft = int(ft.replace('\'', ''))
                inches = int(inches.replace('"', ''))

                height = (ft / 3.281) + (inches / 39.37)
            elif li.re(helpers.re_compile('weight:')):
                weight = int(text.split(' ')[0])
            elif li.re(helpers.re_compile('reach:')):
                reach = int(text.replace('"', ''))
            elif li.re(helpers.re_compile('stance:')):
                stance = text
            elif li.re(helpers.re_compile('dob:')):
                dob = datetime.strptime(text, '%b %d, %Y').date()

        return height, weight, reach, stance, dob
