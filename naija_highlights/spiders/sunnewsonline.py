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
from helpers import *


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


def preprocess_author_and_body(body):
    """ extract author from author or body """
    
    def extract_author(kw, query_string):
        """extract author from query string"""
        index = query_string.index(kw)
        author = query_string[index:]
        author = clean_words(query_string.split(kw)[-1])
        return author
    
    key_words = ["By", "From"]
    body_content = []
    author = None
    
    for i, line in enumerate(body):
        for kw in key_words:
            if kw in line and author is None:
                author = body.pop(i)
                author = author.split("<em>")[0]
                author = clean_html(author)
                author = extract_author(kw, author)
        
        if (not any([i in line for i in key_words])) and line:
            body_content.append(clean_words(clean_html(line)))
        
    author = "Anonymous" if author is None else author
    
    return body_content, author


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
        
        body = response.css(".post-content").xpath("p").getall()
        body, author = preprocess_author_and_body(body)
        
        post["author"] = author
        post["body"] = body
        post["spider"] = self.name
        
        # ascertain that post was created this week
        if week_number == self.this_week:
            if response.url not in self.scraped_links:
                self.scraped_links.append(response.url)
                yield post