# UFC Stats Scraper

Crawls and parses [ufcstats](http://www.ufcstats.com) 
into a [Postgresql](https://www.postgresql.org/) database.

## Prerequisites
* [Python 3.7](https://www.python.org/downloads/)
* [PostgreSQL](https://www.postgresql.org/)

## Install

```commandline
git clone https://github.com/clueshh/ufcstats.git
cd ufcstats
pip install -r requirements.txt
```

## Usage

Provides two [Scrapy Spiders](https://docs.scrapy.org/en/latest/topics/spiders.html),
[EventSpider](ScrapeUFC/spiders/EventSpider.py) and [FightersSpider](ScrapeUFC/spiders/FightSpider.py) 
that scrape the events and fighters pages.

* [ufcstats.com/statistics/events/completed?page=all](http://www.ufcstats.com/statistics/events/completed?page=all)
* [ufcstats.com/statistics/fighters?char=a&page=all](http://www.ufcstats.com/statistics/fighters?char=a&page=all)

The database interactions are in [sqlalchemy](https://www.sqlalchemy.org/) with the schema defined in
[models.py](Database/models.py).

To modify the database uri you can edit the [config.ini](Database/config.ini) file.

```ini
[postgresql]
user=postgres
password=admin
host=localhost
```

The default table name `ufcstats` can be changed in the file [Database.py](Database/Database.py) 
by changing the declaration below.

```python
current_database = 'ufcstats'
```

To begin scraping run [main.py](ScrapeUFC/main.py).
