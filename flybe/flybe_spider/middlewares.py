# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
import json
import random
import logging
import traceback

import requests
from scrapy import signals

from flybe_spider import settings


class StatisticsItem(object):
    def __init__(self):
        self.interval = 0
        self.itemsprev = 0

    # 统计每分钟item
    def process_request(self, request, spider):
        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            items = spider.crawler.stats.get_value('item_scraped_count', 0)
            irate = items - self.itemsprev
            self.itemsprev = items
            spider.crawler.stats.set_value('permins', irate)


class ProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0

    def process_response(self, request, response, spider):
        if response.status == 403:
            spider.log('403 error..', 40)
            spider.is_ok = False
            # spider.log('error ip: %s' % request.meta.get('proxy'), 40)
            return request
        return response

    def process_request(self, request, spider):
        if spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)

    def _get_proxy(self, spider):
        if spider.is_ok:
            self.proxyCount = 0
            return self.proxy
        if self.proxyCount < 8:
            self.proxyCount = self.proxyCount + 1
            logging.info('using old proxy:' + self.proxy)
            return self.proxy

        self.proxyCount = 0
        if self.backSelfCount >= 10:
            #try 10 times and back to sel ip
            logging.info('using self ip')
            self.backSelfCount = 0
            self.proxy = ''
            return self.proxy

        try:
            spider.log('get proxy: ', 40)
            params = {'carrier': spider.name}
            li = json.loads(requests.get(settings.GET_PROXY_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text)
            self.proxy = random.choice(li).decode('ascii') or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''

if __name__ == '__main__':
    p = ProxyMiddleware()
    print(p._get_proxy())
