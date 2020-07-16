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

To start you must have a postgresql database server setup.
Update the database credentials in the [config.ini](Database/config.ini) file.

```ini
[postgresql]
user=postgres
password=admin
host=localhost
```

The default database name `ufcstats` can be changed in the file [Database.py](Database/Database.py) 
by changing the declaration below.

```python
current_database = 'ufcstats'
```

By default the database and all tables will be created if they do not exist.

<hr>

Running the file [main.py](ScrapeUFC/main.py) will scrape all of the the fighters, fights and events from pages below:

* [ufcstats.com/statistics/fighters?char=a&page=all](http://www.ufcstats.com/statistics/fighters?char=a&page=all)
* [ufcstats.com/statistics/events/completed?page=all](http://www.ufcstats.com/statistics/events/completed?page=all)

In the current setup all of the fights will be scraped and added into the database (or updated it they already exist)
Only the events which are not in the `Events` table will be scraped.

All of the database interactions are in [sqlalchemy](https://www.sqlalchemy.org/) with the database schema defined in
[models.py](Database/models.py).
