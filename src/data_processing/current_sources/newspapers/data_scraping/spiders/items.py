# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class NaijaHighlightsItem(scrapy.Item):
    # define the fields for your item here like:
    weblink = scrapy.Field()
    title = scrapy.Field()
    postdate = scrapy.Field()
    thumbnaillink = scrapy.Field()
    author = scrapy.Field()
    body = scrapy.Field()
    spider = scrapy.Field()
    
