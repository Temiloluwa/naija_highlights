import sys
import logging
import pytz
import re
import os
import scrapy
from scrapy.spiders import CrawlSpider
from typing import Tuple
from datetime import datetime
from naija_highlights.items import NaijaHighlightsItem


def setup_logger(logger):
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'logs')
    log_format = logging.Formatter("%(asctime)s %(filename)-12s %(levelname)-8s %(message)s")
    os.makedirs(log_dir, exist_ok=True)
    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(log_format)
    logger.addHandler(stream_handler)
    file_handler = logging.FileHandler(os.path.join(log_dir, f"logfile.log"))
    file_handler.setFormatter(file_handler)
    logger.addHandler(file_handler)
    return logger

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
    name = "sunnewsonline"
    this_week = get_this_week()
    max_page = 4
    scraped_links = []


    def __init__(self):
        logger = setup_logger(logging.getLogger(self.name))

    def start_requests(self):
        all_requests = []
        all_requests.extend([  
            scrapy.Request(f"https://sunnewsonline.com/category/national/page/{pg}", callback=self.parse)
            for pg in range(1, self.max_page + 1)
            ])
        all_requests.extend([  
            scrapy.Request(f"https://sunnewsonline.com/category/columns/page/{pg}", callback=self.parse)
            for pg in range(1, self.max_page + 1)
            ])
        all_requests.extend([  
            scrapy.Request(f"https://sunnewsonline.com/category/business/page/{pg}", callback=self.parse)
            for pg in range(1, self.max_page + 1)
            ])
        all_requests.extend([  
            scrapy.Request(f"https://sunnewsonline.com/category/politics/page/{pg}", callback=self.parse)
            for pg in range(1, self.max_page + 1)
            ])
        all_requests.extend([  
            scrapy.Request(f"https://sunnewsonline.com/category/opinion/page/{pg}", callback=self.parse)
            for pg in range(1, self.max_page + 1)
            ])
        all_requests.extend([  
            scrapy.Request(f"https://sunnewsonline.com/category/entertainment/page/{pg}", callback=self.parse)
            for pg in range(1, self.max_page + 1)
            ])
        all_requests.extend([  
            scrapy.Request(f"https://sunnewsonline.com/category/sporting-sun/page/{pg}", callback=self.parse)
            for pg in range(1, self.max_page + 1)
            ])
        
        return all_requests


    def parse(self, response):
        page_post_links = response.css(".archive-grid-single").xpath("@href").getall()
        return response.follow_all(page_post_links, self.parse_national)
       

    def parse_national(self, response):
        post = NaijaHighlightsItem()
        post["weblink"] = response.url
        post["title"] = response.css(".post-title::text").get()
        dt = preprocess_postdate(response.css(".post-date::text").getall()[-1])
        _, week_number, _ = dt.isocalendar()
        post["postdate"] = (dt.day, dt.month, dt.year) 
        post["thumbnaillink"] = response.xpath("//article/figure/img/@src").get()
        post["author"] = proprecess_author(response)
        post["body"] = response.css(".post-content").xpath("p").getall()
        post["spider"] = self.name
        
        # ascertain that post was created this week
        if week_number == self.this_week:
            if response.url not in self.scraped_links:
                self.scraped_links.append(response.url)
                yield post