from datetime import datetime

from Database.models import Location
from ScrapeUFC.util import BaseParser


class EventParser(BaseParser):
    def __init__(self, event_id, response, db):
        super().__init__(response, db)

        self.event_id = event_id
        self.base_url = self.domain + '/event-details'

        self.event_name = self.response.css('.b-content__title-highlight::text').get().strip()
        li = self.response.css('.b-list__box-list li')
        date_str, location, attendance = [x.strip() for x in li.css('*::text').getall()[2::3]]
        self.date_obj = datetime.strptime(date_str, '%B %d, %Y').date()
        self.location_id = self.get_location_id(location)
        try:
            self.attendance = int(attendance.replace(',', ''))
        except ValueError:
            self.attendance = None

    def serialize(self):
        return dict(id=self.event_id,
                    name=self.event_name,
                    date=self.date_obj,
                    attendance=self.attendance,
                    location_id=self.location_id)

    def get_location_id(self, location):
        """
        Takes a string formatted either:
            'city, region, country' or
            'city, country'

        and returns a valid location_id

        :param location: the location string
        :return int location_id:
        """

        split = location.split(',')
        if len(split) == 3:
            location_dict = {'city': split[0], 'region': split[1], 'country': split[2]}
        elif len(split) == 2:
            location_dict = {'city': split[0], 'region': None, 'country': split[1]}
        else:
            raise ValueError(f'Location [{location}] must be split int size 2 or 3.')

        query = self.db.session.query(Location.id).filter_by(**location_dict)
        if query.scalar() is not None:  # location exists
            location_id = query.first()[0]
        else:  # location doesnt exist
            location = Location(**location_dict)

            self.db.session.add(location)
            self.db.session.flush()
            self.db.session.refresh(location)

            location_id = location.id

        return location_id
