from scrapeUFC.spiders import UFCSpider
from scrapy.crawler import CrawlerProcess

if __name__ == '__main__':
    process = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
    })

    process.crawl(UFCSpider)
    process.start()
