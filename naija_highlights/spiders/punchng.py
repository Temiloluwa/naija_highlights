import re
from typing import Tuple
from datetime import datetime
from scrapy.spiders import SitemapSpider
from naija_highlights.items import NaijaHighlightsItem
from naija_highlights.helpers import *

def preprocess_body(body: str) -> str:
    """ preprocess body """
    return list(map(clean_words, map(clean_html, body)))


def preprocess_postdate(dt: str) -> Tuple[int, int, int]:
    """ preprocess post date """
    dt = dt.strip("\n").strip(" ")
    dt = re.sub(r'(th)|(st)|(nd)', '', dt)
    dt = datetime.strptime(dt, '%d %B %Y')
    return dt


def preprocess_author(author: str) -> str:
    """ preprocess author """
    return author if author is not None else "Anonymous"


class PunchNgSpider(SitemapSpider):
    name = "punchng"
    sitemap_urls = ["https://punchng.com/sitemap_index.xml"]
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
        post["author"] = preprocess_author(
            response.xpath("//span[@class='post-author']/a/text()").get())
        post["body"] = preprocess_body(
            article.css(".post-content").xpath("p").getall())
        post["spider"] = self.name

        # ascertain that post was created this week
        if week_number == self.this_week:
            yield post
    
