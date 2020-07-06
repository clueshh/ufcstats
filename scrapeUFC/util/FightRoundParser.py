from scrapeUFC.util import BaseFightParser


class FightRoundParser(BaseFightParser):
    def __init__(self, fight_id, response, session):
        super().__init__(fight_id, response, session)

        tables = self.response.css('table.b-fight-details__table.js-fight-table')

        if len(tables) == 2:
            self.table1, self.table2 = tables
            self.table_rows = [self.table1.css('tbody tr'), self.table2.css('tbody tr')]

            self.table_cols = [
                ['FIGHTER', 'KD', 'SIG. STR.', 'SIG. STR. %', 'TOTAL STR.', 'TD', 'TD %', 'SUB. ATT', 'PASS', 'REV'],
                ['FIGHTER',	'SIG. STR', 'SIG. STR. %', 'HEAD', 'BODY', 'LEG', 'DISTANCE', 'CLINCH', 'GROUND']
            ]

            self.fighter_a_rounds = self.get_rounds(0)
            self.fighter_b_rounds = self.get_rounds(1)
            self.fight_info = self.fighter_a_rounds + self.fighter_b_rounds
        else:
            self.fight_info = []

    def serialize(self):
        return self.fight_info

    @staticmethod
    def get_col_text(row, index):
        col = row.css(f'td:nth-child({index})')
        col_text = col.css('p.b-fight-details__table-text::text').getall()
        assert len(col_text) == 2
        return col_text

    def get_col_index(self, i, col_name):
        assert col_name in self.table_cols[i], f"Column name: '{col_name}' not in list"
        return self.table_cols[i].index(col_name) + 1

    class ParserHelper:
        def __init__(self):
            pass  # finish this

    def get_rounds(self, fighter_index):
        assert fighter_index in [0, 1]
        fighter_id = self.fighter_a_id if fighter_index == 0 else self.fighter_b_id

        # first table
        kd = self.get_col(fighter_index, 0, 'KD', self.parse_int)
        sig_str, sig_str_attempts = self.get_col(fighter_index, 0, 'SIG. STR.', self.col_x_of_y)
        total_str, total_str_attempts = self.get_col(fighter_index, 0, 'TOTAL STR.', self.col_x_of_y)
        td, td_attempts = self.get_col(fighter_index, 0, 'TOTAL STR.', self.col_x_of_y)
        sub_att = self.get_col(fighter_index, 0, 'SUB. ATT', self.parse_int)
        pass_ = self.get_col(fighter_index, 0, 'PASS', self.parse_int)
        rev = self.get_col(fighter_index, 0, 'REV', self.parse_int)

        # second table
        head, head_attempts = self.get_col(fighter_index, 1, 'HEAD', self.col_x_of_y)
        body, body_attempts = self.get_col(fighter_index, 1, 'BODY', self.col_x_of_y)
        leg, leg_attempts = self.get_col(fighter_index, 1, 'LEG', self.col_x_of_y)
        distance, distance_attempts = self.get_col(fighter_index, 1, 'DISTANCE', self.col_x_of_y)
        clinch, clinch_attempts = self.get_col(fighter_index, 1, 'CLINCH', self.col_x_of_y)
        ground, ground_attempts = self.get_col(fighter_index, 1, 'GROUND', self.col_x_of_y)

        rounds = []
        for i, round_ in enumerate(zip(kd, sig_str, sig_str_attempts, total_str, total_str_attempts,
                                       td, td_attempts, sub_att, pass_, rev, head, head_attempts,
                                       body, body_attempts, leg, leg_attempts, distance, distance_attempts,
                                       clinch, clinch_attempts, ground, ground_attempts), 1):

            rounds.append(dict(fight_id=self.fight_id, fighter_id=fighter_id, round=i,
                               kd=round_[0],
                               sig_str=round_[1],
                               sig_str_attempts=round_[2],
                               total_str=round_[3],
                               total_str_attempts=round_[4],
                               td=round_[5],
                               td_attempts=round_[6],
                               sub_att=round_[7],
                               pass_=round_[8],
                               rev=round_[9],
                               head=round_[10],
                               head_attempts=round_[11],
                               body=round_[12],
                               body_attempts=round_[13],
                               leg=round_[14],
                               leg_attempts=round_[15],
                               distance=round_[16],
                               distance_attempts=round_[17],
                               clinch=round_[18],
                               clinch_attempts=round_[19],
                               ground=round_[20],
                               ground_attempts=round_[21]))

        return rounds

    def get_col(self, fighter_index, table_index, col_name, callback):
        rounds = []
        for row in self.table_rows[table_index]:
            col_text = self.get_col_text(row, self.get_col_index(table_index, col_name))
            rounds.append(col_text[fighter_index].strip())

        return callback(rounds)

    @staticmethod
    def parse_int(list_text):
        return [int(x) for x in list_text]

    @staticmethod
    def col_x_of_y(list_text):
        def parse_x_of_y(text):
            spl = text.split(' of ')
            assert len(spl) == 2
            return [int(x) for x in spl]

        all_ = [parse_x_of_y(text) for text in list_text]
        return [row[0] for row in all_], [row[1] for row in all_]
