# -*- coding: utf-8 -*-
import time, logging, json, requests

from lamudatech_dev import settings
from utils.push_date import push_date


class LamudatechDevPipeline(object):
    def __init__(self):
        self.store = []
        self.interval = 0
        self.item_interval = 0

    def process_item(self, item, spider):
        # 加入心跳
        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            permins = spider.crawler.stats.get_value('permins')
            print(self.heartbeat(spider.host_name, spider.spider_name, spider.num, permins, spider.version))

        item = self.keys_for_short(item)
        self.store.append(item)
        run_time = time.time()
        num = len(self.store)
        if num >= 10 or run_time - self.item_interval >= 10:
            self.item_interval = run_time
            # 正式api
            post_api = settings.PUSH_DATA_URL
            status = push_date(post_api, {'carrier': item["cr"]}, 'add', self.store, spider.host_name)
            if status:
                spider.log((status, num), level=20)
                self.store = []

    @staticmethod
    def heartbeat(name, carrier, num, permins, version=1.0):
        params = {
            'carrier': carrier,
            'num': num,
            'name': name,
            'permins': permins,
            'version': version,
        }
        try:
            return requests.get(settings.HEARTBEAT_URL, params=params, timeout=180).text
        except Exception as e:
            logging.error(e)

    @staticmethod
    def keys_for_short(data):
        item = {}
        for long, short in settings.KEYS_SHORT.items():
            if long in data:
                item[short] = data.get(long)
        return item


# 仅供测试用
class LamudatechDevPipelineTest(object):
    def __init__(self):
        self.store = []
        self.interval = 0

    def process_item(self, item, spider):
        # 加入心跳
        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            permins = spider.crawler.stats.get_value('permins')
            print(self.heartbeat(spider.host_name, spider.spider_name, spider.num, permins, spider.version))

        item = self.keys_for_short(item)
        self.store.append(item)
        num = len(self.store)
        if 1 or num >= 10:
            # 测试api
            post_api = settings.PUSH_DATA_URL_TEST
            status = push_date(post_api, {'carrier': item["cr"]}, 'add', self.store, spider.host_name)
            # status = push_date(post_api, {'carrier': 'SL'}, 'add', self.store)
            if status:
                spider.log((status, num), level=20)
                self.store = []

    @staticmethod
    def heartbeat(name, carrier, num, permins, version=1.0):
        params = {
            'carrier': carrier,
            'num': num,
            'name': name,
            'permins': permins,
            'version': version
        }
        try:
            return requests.get(settings.HEARTBEAT_URL, params=params, timeout=180).text
        except Exception as e:
            logging.error(e)

    @staticmethod
    def keys_for_short(data):
        item = {}
        for long, short in settings.KEYS_SHORT.items():
            if long in data:
                item[short] = data.get(long)
        return item
