# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
import json
import random
import traceback

import requests
from scrapy import signals

from a7c_spider import settings


class ProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0
        self.is_ok = True

    def process_response(self, request, response, spider):
        status = response.status
        if status == 404:
            self.is_ok = False
            self.proxy = self._get_proxy(spider)
            spider.log('response: %s' % status, 20)
            # spider.log(request.meta.get('proxy'), 20)
            return request
        self.is_ok = True
        return response

    def process_request(self, request, spider):
        if hasattr(spider, 'proxy') and spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)

    def _get_proxy(self, spider):
        if self.is_ok and spider.is_ok:
            return self.proxy
        if self.proxyCount < settings.CONCURRENT_REQUESTS:
            self.proxyCount = self.proxyCount + 1
            spider.log('using old proxy:' + self.proxy, 20)
            return self.proxy

        self.proxyCount = 0
        if self.backSelfCount >= 5:
            #try 10 times and back to sel ip
            spider.log('using self ip', 20)
            self.backSelfCount = 0
            self.proxy = ''
            return self.proxy

        try:
            params = {'carrier': 'BE'}
            li = json.loads(requests.get(settings.GET_PROXY_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text)
            spider.log('Proxy Num: ' + str(len(li)), 20)
            spider.log(str(li), 20)
            self.proxy = random.choice(li).decode('ascii') or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            traceback.print_exc()
            spider.log('get proxy error....', 20)
        finally:
            return self.proxy or ''


class A7CSpiderDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class StatisticsItem(object):
    def __init__(self):
        self.interval = 0
        self.itemsprev = 0

    # 统计每分钟item
    def process_request(self, request, spider):
        run_time = time.time()
        if  run_time - self.interval >= 60:
            self.interval = run_time
            items = spider.crawler.stats.get_value('item_scraped_count', 0)
            irate = items - self.itemsprev
            self.itemsprev = items
            spider.crawler.stats.set_value('permins', irate)