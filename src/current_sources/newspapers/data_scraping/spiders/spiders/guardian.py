import sys
import logging
import pytz
import re
import os
from typing import Tuple
from datetime import datetime
from scrapy.spiders import SitemapSpider
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

class GuardianNg(SitemapSpider):
    name = "guardian"
    sitemap_urls = ["https://guardian.ng/sitemap.xml"]
    this_week = get_this_week()

    def sitemap_filter(self, entries):
        for entry in entries:
            _, publish_week, _ = localize_time(datetime.\
                    strptime(entry['lastmod'], '%Y-%m-%dT%X%z')).isocalendar()
            if publish_week == self.this_week:
                yield entry


    def parse(self, response):
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
    
