 # Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
import os
from itemadapter import ItemAdapter
from scrapy.exporters import JsonLinesItemExporter


class NaijaHighlightsPipeline:
    root = os.path.join(os.path.dirname(__file__), 'data', 'bronze')
    def open_spider(self, spider):
        self.day_export = {}

    def close_spider(self, spider):
        self.file.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        day = adapter["postdate"]
        if day not in self.day_export:
            _dir = os.path.join(self.root, day)
            os.makedirs(_dir, exist_ok=True)
            json_file = open(_dir, "items.json", 'wb')
            exporter = JsonLinesItemExporter(json_file)
            exporter.start_exporting()
            self.day_export[day] = (exporter, json_file)

        return 