import os
from datetime import datetime

from scrapy.crawler import CrawlerProcess

from ScrapeUFC.spiders import UFCSpider

if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'LOG_LEVEL': 'INFO',  # 'DEBUG'
        'LOG_FILE': os.path.join('logs', datetime.now().strftime('%Y-%m-%d %H%M%S') + ' scrapy.log')
    })

    process.crawl(UFCSpider)
    process.start()
