BOT_NAME = "fixprice_parser"

SPIDER_MODULES = ["fix_price_spider.spiders"]
NEWSPIDER_MODULE = "fix_price_spider.spiders"

ALLOWED_DOMAINS = ["fix-price.com"]
START_URLS = [
    "https://fix-price.com/catalog/kosmetika-i-gigiena",
    "https://fix-price.com/catalog/bytovaya-khimiya",
    "https://fix-price.com/catalog/pochti-darom"
]

ROBOTSTXT_OBEY = False

COOKIES_ENABLED = True

COOKIES = {
    "locality": "%7B%22city%22%3A%22%D0%95%D0%BA%D0%B0%D1%82%D0%B5%D1%80%D0%B8%D0%BD%D0%B1%D1%83%D"
    "1%80%D0%B3%22%2C%22cityId%22%3A55%2C%22longitude%22%3A60.597474%2C%22latitude%22"
    "%3A56.838011%2C%22prefix%22%3A%22%D0%B3%22%7D"
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
