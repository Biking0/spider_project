# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import time
import json
import random
import logging

import requests

from example import settings


class F3TokenMiddleware(object):
    token = None
    invalid_status = [401, 403]

    def __init__(self):
        self.proxy = ''
        self.proxy_count = 0
        self.back_self_count = 0
        self.is_ok = True

    def _get_token(self, spider):
        headers = spider.custom_settings.get('DEFAULT_REQUEST_HEADERS')
        url = spider.token_url
        while True:
            try:
                if self.proxy:
                    proxies = {
                        'http': 'http://%s' % self.proxy,
                        'https': 'https://%s' % self.proxy
                    }
                    res = requests.post(
                            url, headers=headers, proxies=proxies, timeout=settings.DOWNLOAD_TIMEOUT, verify=False)
                else:
                    res = requests.post(url, headers=headers, timeout=settings.DOWNLOAD_TIMEOUT, verify=False)
                if res.status_code in self.invalid_status:
                    time.sleep(2)
                    continue
                token = res.headers.get('x-session-token')
                self.is_ok = True
                return token
            except Exception as e:
                self.is_ok = False
                self.proxy = self._get_proxy(spider)
                print(e)
                time.sleep(2)

    def process_response(self, request, response, spider):
        if response.status in self.invalid_status:
            self.is_ok = False
            return request
        self.is_ok = True
        return response

    def process_request(self, request, spider):
        if not self.token:
            self.token = self._get_token(spider)
            print(self.token)
            spider.log('got token', 20)
        request.headers['x-session-token'] = self.token
        # print request.headers
        if hasattr(spider, 'proxy') and spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)

    def _get_proxy(self, spider):
        num = spider.custom_settings.get('PROXY_TRY_NUM', 10)
        if self.is_ok and spider.is_ok:
            self.proxy_count = 0
            return self.proxy
        if self.proxy_count < num:
            self.proxy_count = self.proxy_count + 1
            logging.info('using old proxy:' + self.proxy)
            return self.proxy

        self.proxy_count = 0
        if self.back_self_count >= 10:
            #try 10 times and back to sel ip
            logging.info('using self ip')
            self.back_self_count = 0
            self.proxy = ''
            return self.proxy

        try:
            params = {'carrier': spider.name}
            li = json.loads(requests.get(settings.GET_PROXY_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text)
            logging.info('Proxy Num: ' + str(len(li)))
            logging.info(str(li))
            self.proxy = random.choice(li).decode('ascii') or ''
            self.back_self_count = self.back_self_count + 1
        except Exception as e:
            # traceback.print_exc()
            logging.info('get proxy error....%s' % e, 40)
        finally:
            return self.proxy or ''


class StatisticsItem(object):
    def __init__(self):
        self.interval = 0
        self.item_spr = 0

    # 统计每分钟item
    def process_request(self, request, spider):
        run_time = time.time()
        if run_time - self.interval >= 60:
            self.interval = run_time
            items = spider.crawler.stats.get_value('item_scraped_count', 0)
            irate = items - self.item_spr
            self.item_spr = items
            spider.crawler.stats.set_value('permins', irate)

