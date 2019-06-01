# -*- coding: utf-8 -*-
import requests, logging, json, time
from a7c_spider import settings


class A7CSpiderPipeline(object):
    def __init__(self):
        self.store = []
        self.interval = 0

    def process_item(self, item, spider):
        # 加入心跳
        # item['segments'] = '[]'
        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            permins = spider.crawler.stats.get_value('permins')
            print(self.heartbeat(spider.host_name, '7C', spider.num, permins, spider.version))

        self.store.append(dict(item))
        num = len(self.store)
        if num >= 15:
            # 测试api
            # post_api = '%scarrier=%s' % (settings.PUSH_DATA_URL_TEST, item["carrier"])
            # 正式api
            post_api = '%scarrier=%s' % (settings.PUSH_DATA_URL, item["carrier"])
            data = {
                "action": "add",
                "data": self.store
            }
            try:
                response = requests.post(post_api, data=json.dumps(data),
                                         timeout=180)
                self.store = []
                logging.info((response.content, num))
            except Exception as e:
                logging.error(e)

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
