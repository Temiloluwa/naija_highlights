 # Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
from itemadapter import ItemAdapter


class NaijaHighlightsPipeline:
    filename = os.path.join(os.path.dirname(__file__),
                     'data', 'bronze','items.json')
    def open_spider(self, spider):
        self.file = open(self.filename, 'w')

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + "\n"
        self.file.write(line)
        return item