import pytz
import re
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
    return dt.day, dt.month, dt.year

class PunchNgSpider(SitemapSpider):
    name = "punchng"
    sitemap_urls = ["https://punchng.com/sitemap-posttype-post.2023.xml"]

    def sitemap_filter(self, entries):
        _, this_week, _ = localize_time(datetime.today()).isocalendar()
        for entry in entries:
            _, publish_week, _ = localize_time(datetime.\
                    strptime(entry['lastmod'], '%Y-%m-%dT%X%z')).isocalendar()
            if publish_week == this_week:
                yield entry
            

    def parse(self, response):
        post = NaijaHighlightsItem()
        article =  response.css(".single-article")
        post["weblink"] = response.url
        post["title"] = article.css("h1::text").get()
        post["postdate"] = preprocess_postdate(article.css(".post-date::text").get())
        post["thumbnaillink"] = response.xpath("//figure/img/@src").get()
        post["author"] = response.xpath("//span[@class='post-author']/a/text()").get()
        post["body"] = article.css(".post-content").xpath("p").getall()

        yield post
    
