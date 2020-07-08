import re
from datetime import datetime

from sqlalchemy import func

from Database.models import WeightClasses
from ScrapeUFC.util import helpers, BaseFightParser


class FightParser(BaseFightParser):
    def __init__(self, db, response, fight_id):
        super().__init__(db, response, fight_id)

        self.details = self.response.css('div.b-fight-details__fight')

    def serialize(self):
        title_bout, fotn_bonus, performance_bonus, sub_bonus, ko_bonus = self.get_title_bonus()

        return dict(fight_table=dict(id=self.fight_id,
                                     fighter_a_id=self.fighter_a_id,
                                     fighter_b_id=self.fighter_b_id,
                                     event_id=self.get_event_id(),
                                     weight_class_id=self.get_weight_class_id(),
                                     winner=self.get_fight_winner(),
                                     gender=self.get_gender(),
                                     method=self.get_method(),
                                     finish_round=self.get_finish_round(),
                                     finish_time=self.get_finish_time(),
                                     scheduled_rounds=self.get_scheduled_rounds(),
                                     overtime_rounds=self.get_ot_rounds(),
                                     referee=self.get_referee(),
                                     details=self.get_details(),
                                     title_bout=title_bout,
                                     fotn_bonus=fotn_bonus,
                                     performance_bonus=performance_bonus,
                                     sub_bonus=sub_bonus,
                                     ko_bonus=ko_bonus,
                                     time_format=self.get_time_format()),
                    rounds_table=self.get_rounds())

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

        result = self.db.session.query(WeightClasses.id,
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

    def get_finish_round(self):
        return int(self.details.xpath("//*[contains(text(), 'Round:')]/..").css('*::text').extract()[-1].strip())

    def get_finish_time(self):
        t = self.details.xpath("//*[contains(text(), 'Time:')]/..").css('*::text').extract()[-1].strip()
        return datetime.strptime(t, '%M:%S').time()

    def get_ot_rounds(self):
        time_format = self.get_time_format()
        if time_format == 'No Time Limit':
            return 0
        else:
            m1 = re.search(r"\d+OT", time_format)  # fight has more than one OT
            m2 = re.search("OT", time_format)  # fight has one OT
            if m1:
                num_ot = int(time_format[m1.start(0): m1.end(0) - 2])
            elif m2:
                num_ot = 1
            else:
                num_ot = 0

            return num_ot

    def get_scheduled_rounds(self):
        time_format = self.get_time_format()
        if time_format == 'No Time Limit':
            return -1
        else:
            try:
                return int(time_format.split(' ')[0])
            except ValueError:
                raise ValueError(f'No valid parser for \'{time_format}\'')

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
            img_name = image.css('img::attr(src)').get().split('/')[-1]
            if img_name == 'perf.png':
                perf = True
            elif img_name == 'belt.png':
                belt = True
            elif img_name == 'fight.png':
                fight = True
            elif img_name == 'sub.png':
                sub = True
            elif img_name == 'ko.png':
                ko = True
            else:
                raise ValueError(f'Unknown image {img_name}')

        return belt, perf, fight, sub, ko

    def get_rounds(self):
        tables = self.response.css('table.b-fight-details__table.js-fight-table')
        if len(tables) == 0:
            return []

        table1_rows, table2_rows = tables[0].css('tbody tr'), tables[1].css('tbody tr')

        rounds = []
        for fighter_index in [0, 1]:
            for round_, (table1_row, table2_row) in enumerate(zip(table1_rows, table2_rows), 1):
                rounds.append(self.get_fighter_round(table1_row, table2_row, fighter_index, round_))

        return rounds

    def is_overtime(self, round_):
        num_ot = self.get_ot_rounds()
        total_rounds = self.get_total_rounds()

        if total_rounds:
            return True if round_ > (total_rounds - num_ot) else False
        else:
            return False

    def get_round_split(self):
        time_format = self.get_time_format()

        if time_format == 'No Time Limit':
            return None

        m = re.search("[(].*[)]", time_format)
        assert m, f'time_format: {time_format} should have parenthesis'
        return m[0][1:-1].split('-')

    def get_total_rounds(self):
        spl = self.get_round_split()
        return len(spl) if spl else -1

    def get_scheduled_round_length(self, round_):
        spl = self.get_round_split()
        if spl:
            round_time = spl[round_ - 1]
            return datetime.strptime(round_time, "%M").time()
        else:
            return datetime.strptime('0', "%M").time()

    def get_actual_round_length(self, round_):
        if self.get_finish_round() == round_:
            return self.get_finish_time()
        else:
            return self.get_scheduled_round_length(round_)

    def get_fighter_round(self, table1_row, table2_row, fighter_index, round_):
        helper = self.RoundHelper(table1_row, table2_row, fighter_index)

        return dict(fight_id=self.fight_id,
                    fighter_id=self.fighter_a_id if fighter_index == 0 else self.fighter_b_id,
                    round=round_,
                    kd=helper.get_kd(),
                    sig_str=helper.get_sig_str(False),
                    sig_str_attempts=helper.get_sig_str(True),
                    total_str=helper.get_total_str(False),
                    total_str_attempts=helper.get_total_str(True),
                    td=helper.get_td(False),
                    td_attempts=helper.get_td(True),
                    sub_att=helper.get_sub_att(),
                    pass_=helper.get_pass(),
                    rev=helper.get_rev(),
                    head=helper.get_head(False),
                    head_attempts=helper.get_head(True),
                    body=helper.get_body(False),
                    body_attempts=helper.get_body(True),
                    leg=helper.get_leg(False),
                    leg_attempts=helper.get_leg(True),
                    distance=helper.get_distance(False),
                    distance_attempts=helper.get_distance(True),
                    clinch=helper.get_clinch(False),
                    clinch_attempts=helper.get_clinch(True),
                    ground=helper.get_ground(False),
                    ground_attempts=helper.get_ground(True),
                    overtime=self.is_overtime(round_),
                    scheduled_round_length=self.get_scheduled_round_length(round_),
                    actual_round_length=self.get_actual_round_length(round_))

    class RoundHelper:
        def __init__(self, table1_row, table2_row, fighter_index):
            self.fighter_index = fighter_index

            self.table_info = dict(
                table1=dict(cols=['FIGHTER', 'KD', 'SIG. STR.', 'SIG. STR. %',
                                  'TOTAL STR.', 'TD', 'TD %', 'SUB. ATT', 'PASS', 'REV'],
                            row=table1_row),
                table2=dict(cols=['FIGHTER', 'SIG. STR', 'SIG. STR. %', 'HEAD',
                                  'BODY', 'LEG', 'DISTANCE', 'CLINCH', 'GROUND'],
                            row=table2_row)
            )

        def get_factory(self, col_name, key):
            table_info = self.table_info[key]

            column_index = self.get_col_index(table_info['cols'], col_name)
            return self.get_col_text(table_info['row'], column_index)[self.fighter_index]

        def get_kd(self):
            return int(self.get_factory('KD', 'table1'))

        def get_sig_str(self, attempts):
            col_text = self.get_factory('SIG. STR.', 'table1')
            return self.split_x_of_y(col_text, attempts)

        def get_total_str(self, attempts):
            col_text = self.get_factory('TOTAL STR.', 'table1')
            return self.split_x_of_y(col_text, attempts)

        def get_td(self, attempts):
            col_text = self.get_factory('TD', 'table1')
            return self.split_x_of_y(col_text, attempts)

        def get_sub_att(self):
            return int(self.get_factory('SUB. ATT', 'table1'))

        def get_pass(self):
            return int(self.get_factory('PASS', 'table1'))

        def get_rev(self):
            return int(self.get_factory('REV', 'table1'))

        def get_head(self, attempts):
            col_text = self.get_factory('HEAD', 'table2')
            return self.split_x_of_y(col_text, attempts)

        def get_body(self, attempts):
            col_text = self.get_factory('BODY', 'table2')
            return self.split_x_of_y(col_text, attempts)

        def get_leg(self, attempts):
            col_text = self.get_factory('LEG', 'table2')
            return self.split_x_of_y(col_text, attempts)

        def get_distance(self, attempts):
            col_text = self.get_factory('DISTANCE', 'table2')
            return self.split_x_of_y(col_text, attempts)

        def get_clinch(self, attempts):
            col_text = self.get_factory('CLINCH', 'table2')
            return self.split_x_of_y(col_text, attempts)

        def get_ground(self, attempts):
            col_text = self.get_factory('GROUND', 'table2')
            return self.split_x_of_y(col_text, attempts)

        @staticmethod
        def split_x_of_y(x_of_y, attempts):
            spl = x_of_y.split(' of ')
            assert len(spl) == 2
            return int(spl[1]) if attempts else int(spl[0])

        @staticmethod
        def get_col_index(table_cols, col_name):
            assert col_name in table_cols, f"Column name: '{col_name}' not in table_cols"
            return table_cols.index(col_name) + 1

        @staticmethod
        def get_col_text(row_selector, nthchild_index):
            col = row_selector.css(f'td:nth-child({nthchild_index})')
            col_text = col.css('p.b-fight-details__table-text::text').getall()
            assert len(col_text) == 2
            return [text.strip() for text in col_text]
