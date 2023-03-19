import sys
import os
import logging
from itemadapter import ItemAdapter
from scrapy.exporters import JsonLinesItemExporter

log_dir = os.path.join(os.path.dirname(__file__), 'data', 'logs')
log_format = logging.Formatter("%(asctime)s %(filename)-12s %(levelname)-8s %(message)s")
os.makedirs(log_dir, exist_ok=True)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(log_format)
logger.addHandler(stream_handler)
file_handler = logging.FileHandler(os.path.join(log_dir,f"logfile.log"))
file_handler.setFormatter(file_handler)
logger.addHandler(file_handler)

class NaijaHighlightsPipeline:
    root = os.path.join(os.path.dirname(__file__), 'data', 'bronze')
    def open_spider(self, spider):
        self.day_export = {}

    def close_spider(self, spider):
        for exporter, json_file in self.day_export.values():
            exporter.finish_exporting()
            json_file.close()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        day, month, year = adapter["postdate"]
        day_dir = os.path.join(self.root, f"year={year}/month={month}/day={day}")
        if day not in self.day_export:
            os.makedirs(day_dir, exist_ok=True)
            json_file = open(os.path.join(day_dir, "items.json"), 'wb')
        json_file = open(os.path.join(day_dir, "items.json"), 'ab')
        exporter = JsonLinesItemExporter(json_file)
        exporter.start_exporting()
        self.day_export[day] = (exporter, json_file)
        exporter.export_item(item)
        return 