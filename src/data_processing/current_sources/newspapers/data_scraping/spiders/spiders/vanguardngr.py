import sys
import logging
import pytz
import re
import os
import scrapy
from typing import Tuple
from datetime import datetime
from scrapy.spiders import Spider
from scrapy.spiders import XMLFeedSpider
from naija_highlights.items import NaijaHighlightsItem



def localize_time(dt: datetime) -> datetime:
    """ localize time to Lagos """
    if dt.tzinfo:
        return dt.replace(tzinfo=pytz.timezone('Africa/Lagos'))
    return pytz.timezone('Africa/Lagos').localize(dt)


def preprocess_postdate(dt: str) -> Tuple[int, int, int]:
    """ preprocess post date """
    dt = dt.strip("\n").strip(" ")
    dt = re.sub(r'(th)|(st)|(nd)', '', dt)
    dt = datetime.strptime(dt, '%d %B %Y')
    return dt

def get_this_week():
    _, this_week, _ = localize_time(datetime.today()).isocalendar()
    return this_week

class VanguardNgr(XMLFeedSpider):
    name = "vanguardngr"     
    this_week = get_this_week()

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    def start_requests(self):
        yield scrapy.Request('https://www.vanguardngr.com/news-sitemap.xml', 
            callback=self.parse_node,
            headers=self.HEADERS)

    def parse_node(self, response):
        post = NaijaHighlightsItem()
        article =  response.css(".single-article")
        post["weblink"] = response.url
        post["title"] = article.css("h1::text").get()
        dt = preprocess_postdate(article.css(".post-date::text").get())
        _, week_number, _ = dt.isocalendar()
        post["postdate"] = (dt.day, dt.month, dt.year) 
        post["thumbnaillink"] = response.xpath("//figure/img/@src").get()
        post["author"] = response.xpath("//span[@class='post-author']/a/text()").get()
        post["body"] = article.css(".post-content").xpath("p").getall()

        # ascertain that post was created this week
        if week_number == self.this_week:
            yield post
    
