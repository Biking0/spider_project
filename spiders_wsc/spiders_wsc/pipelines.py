# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import time

from utils import pub_util
from utils import data_util
from spiders_wsc import settings


class SpidersWscPipeline(object):
    def __init__(self):
        self.store = []
        self.interval = 0

    def process_item(self, item, spider):
        item = data_util.strip_item(item)
        item = data_util.keys_to_short(item)
        self.store.append(item)

        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            permins = spider.crawler.stats.get_value('permins')
            print(pub_util.heartbeat(spider.host_name, spider.name, spider.num, permins, spider.version))

        num = settings.PUSH_DATA_NUM
        if len(self.store) >= num:
            url = data_util.get_random_url(settings.PUSH_DATA_URL)
            add_success = pub_util.operate_data('add', self.store, url, spider.host_name, carrier=spider.name.upper())
            if add_success:
                self.store = []
                invalid_success = pub_util.operate_data('invalid', spider.task, url + 'carrier=%s' % spider.name,
                                                        spider.host_name, carrier=spider.name.upper)
                if invalid_success:
                    spider.task = []


class SpidersWscPipelineTest(object):
    def __init__(self):
        self.store = []
        self.interval = 0
        self.url = settings.PUSH_DATA_URL_TEST

    def process_item(self, item, spider):
        item = data_util.strip_item(item)
        item = data_util.keys_to_short(item)
        self.store.append(item)

        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            permins = spider.crawler.stats.get_value('permins')
            print(pub_util.heartbeat(spider.host_name, spider.name, spider.num, permins, spider.version))

        num = settings.PUSH_DATA_NUM
        if 1 or len(self.store) >= num:
            add_success = pub_util.operate_data('add', self.store, self.url, spider.host_name,
                                                carrier=spider.name.upper())
            if add_success:
                self.store = []
                invalid_success = pub_util.operate_data('invalid', spider.task, self.url,
                                                        spider.host_name, carrier=spider.name.upper)
                if invalid_success:
                    spider.task = []
