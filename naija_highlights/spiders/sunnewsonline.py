import sys
import logging
import pytz
import re
import os
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from typing import Tuple
from datetime import datetime
from naija_highlights.items import NaijaHighlightsItem

log_dir = os.path.join(os.path.dirname(__file__), 'data', 'logs')
log_format = logging.Formatter("%(asctime)s %(filename)-12s %(levelname)-8s %(message)s")
os.makedirs(log_dir, exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_format)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler(os.path.join(log_dir, f"logfile.log"))
file_handler.setFormatter(file_handler)
logger.addHandler(file_handler)


def localize_time(dt: datetime) -> datetime:
    """ localize time to Lagos """
    if dt.tzinfo:
        return dt.replace(tzinfo=pytz.timezone('Africa/Lagos'))
    return pytz.timezone('Africa/Lagos').localize(dt)


def preprocess_postdate(dt: str) -> Tuple[int, int, int]:
    """ preprocess post date """
    dt = dt.strip("\n").strip(" ")
    dt = re.sub(r'(th)|(st)|(nd)', '', dt)
    try:
        dt = datetime.strptime(dt, '%d %B %Y')
    except Exception as e:
        print("could not parse date with error: ", e)

    return dt

def proprecess_author(response) -> str:
    """ preprocess author """
    try:
        at = response.xpath("//p[@class='p1']/span[@class='s2']/b/text()").get()
        at = at.strip(" ").split(",")[1]
    except AttributeError:
        at = response.css(".post-content").xpath("p/text()").get()
        at = at.strip(" ").split(",")[0]
    except Exception as e:
        print(f"an error occured, {e}")
    
    return at


def get_this_week():
    _, this_week, _ = localize_time(datetime.today()).isocalendar()
    return this_week

class Sunnewsonline(CrawlSpider):
    name = "Sunnewsonline"
    start_urls = ["https://sunnewsonline.com"]
    this_week = get_this_week()
    national_page = 1
    max_page = 4

    rules = (
        Rule(LinkExtractor(allow=("category/national/",)), callback='parse_national'),
    ) 

    def parse_national(self, response):
        page_post_links = response.css(".archive-grid-single").xpath("@href").getall()
        for link in page_post_links:
            yield scrapy.Request(link, callback=self.parse)
        
        self.national_page += 1
        if self.national_page <= self.max_page:
            yield response.follow("https://sunnewsonline.com/category/national/page/{self.national_page}/",
                            self.parse_national)

    def parse(self, response):
        post = NaijaHighlightsItem()
        post["weblink"] = response.url
        post["title"] = response.css(".post-title::text").get()
        dt = preprocess_postdate(response.css(".post-date::text").getall()[-1])
        if dt is None:
            self.logger.info(f'response url: {response.url} has an error')
        _, week_number, _ = dt.isocalendar()
        post["postdate"] = (dt.day, dt.month, dt.year) 
        post["thumbnaillink"] = response.xpath("//article/figure/img/@src").get()
        post["author"] = proprecess_author(response)
        post["body"] = response.css(".post-content").xpath("p").getall()
        post["spider"] = self.name

        # ascertain that post was created this week
        #if week_number == self.this_week:
        yield post
    
