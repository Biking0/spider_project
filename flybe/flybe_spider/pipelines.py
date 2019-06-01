# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from utils.airports import getCityPortsByAPI
import time
from flybe_spider import settings
from utils import pubUtil

class FlybePipeline(object):

    def __init__(self):
        self.cityPorts = getCityPortsByAPI()
        self.store = []
        self.basic_time = 0


    def addCities(self, item):
        if 'fromCity' not in item:
            item['fromCity'] = self.cityPorts.get(item['depAirport'])
        if 'toCity' not in item:
            item['toCity'] = self.cityPorts.get(item['arrAirport'])

    def process_item(self, item, spider):
        self.addCities(item)
        self.store.append(dict(item))
        if time.time() - self.basic_time >= settings.HEARTBEAT_DURATION:
            self.basic_time = time.time()
            permins = spider.crawler.stats.get_value('permins')
            print(pubUtil.heartbeat(spider.host_name, spider.carrier, spider.num, permins, spider.version))
        if len(self.store) >= settings.PUSH_DATA_NUM:
            pubUtil.pushData('add', self.store)
            self.store = []
