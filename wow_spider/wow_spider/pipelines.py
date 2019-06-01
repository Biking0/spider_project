# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from wow_spider import settings
from utils import pubUtil, dataUtil
import time

class LmdSpidersPipeline(object):
    def __init__(self):
        self.store = []
        self.interval = 0

    def process_item(self, item, spider):
        # item['segments'] = '[]'
        item = dataUtil.strip_item(item)
        item = dataUtil.keys_for_short(item)
        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            permins = spider.crawler.stats.get_value('permins')
            print(pubUtil.heartbeat(spider.host_name, spider.name, spider.num, permins, spider.version))

        self.store.append(dict(item))
        
        if hasattr(spider, 'push_data_num'):
            num = spider.push_data_num
        else:
            num = settings.PUSH_DATA_NUM
        if len(self.store) >= num:
            url = dataUtil.get_random_url(settings.PUSH_DATA_URL)
            add_success = pubUtil.addData('add', self.store, url, spider.host_name, carrier=spider.name.upper())
            if add_success:
                if hasattr(spider, 'spe'):
                    push_data_log = ['%s->%s:%s %s' % (data.get('depAirport'), data.get('arrAirport'), time.strftime('%Y-%m-%d', time.localtime(data.get('depTime'))), data.get('flightNumber')) for data in self.store]
                    spider.log('push task :' + str(push_data_log), 20)
                self.store = []
                invalid_success = pubUtil.invalidData('invalid', spider.task, url + 'carrier=%s' % spider.name, spider.host_name)
                if invalid_success:
                    spider.task=[]

class LmdSpidersPipelineTest(object):

    def __init__(self):
        self.store = []
        self.interval = 0

    def process_item(self, item, spider):
        # item['segments'] = '[]'
        item = dataUtil.strip_item(item)
        item = dataUtil.keys_for_short(item)

        self.store.append(dict(item))
        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            permins = spider.crawler.stats.get_value('permins')
            print(pubUtil.heartbeat(spider.host_name, spider.name, spider.num, permins, spider.version))

        if 1 or len(self.store) >= settings.PUSH_DATA_NUM:
            add_success = pubUtil.addData('add', self.store, settings.PUSH_DATA_URL_TEST, spider.host_name, carrier=spider.name.upper())
            if add_success:
                self.store = []
                invalid_success = pubUtil.invalidData('invalid', spider.task, settings.PUSH_DATA_URL_TEST + 'carrier=%s' % spider.name, spider.host_name)
                if invalid_success:
                    spider.task=[]

