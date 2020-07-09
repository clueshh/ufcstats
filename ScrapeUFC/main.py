import os
from datetime import datetime

from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging

from ScrapeUFC.spiders import EventsSpider, FightersSpider


@defer.inlineCallbacks
def crawl():
    yield runner.crawl(FightersSpider)
    yield runner.crawl(EventsSpider)
    reactor.stop()


if __name__ == '__main__':
    settings = {
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': 'INFO',
        'LOG_FILE': os.path.join('logs', datetime.now().strftime("%Y%m%d-%H%M%S") + ' scrapy.log'),
        'COOKIES_ENABLED': False
    }

    configure_logging()
    runner = CrawlerRunner(settings)

    crawl()
    reactor.run()
