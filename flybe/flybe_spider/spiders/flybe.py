# -*- coding: utf-8 -*-
import os
import csv
import json
import time
import random
import urllib
import logging
from datetime import datetime, timedelta

import scrapy
from jsonpath import jsonpath

from flybe_spider.items import FlybeItem
from utils import pubUtil


class FlybeSpider(scrapy.Spider):
    name = 'be'
    allowed_domains = ["flybe.com"]
    is_ok = True
    start_urls = "https://www.flybe.com/api/fares/day/new/"
    carrier = 'BE'
    version = 1.5

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.proxy = True

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.carrier, self.num, permins, self.version))
        result_iter, result = None, None
        while True:
            if hasattr(self, 'local'):
                if not result_iter or not result:
                    result_iter = self.get_task()
                result = next(result_iter)
            else:
                result = pubUtil.getUrl('BE', 10)
            if not result:
                time.sleep(60)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)  # 把获取到的data格式化
                # dt, dep, to = '2018-11-01', 'EXT', 'JER'
                if pubUtil.dateIsInvalid(dt):
                    continue
                temp = {
                    'depart': dep,
                    'arr': to,
                    'departing': dt,
                    'returning': '',
                    'promo-code': '',
                    'adults': 3,
                    'teens': 0,
                    'children': 0,
                    'infants': 0
                }
                try:
                    params = urllib.parse.urlencode(temp)
                except:
                    params = urllib.urlencode(temp)

                url = '%s%s/%s?%s' % (self.start_urls, dep, to, params)
                yield scrapy.Request(
                    url,
                    callback=self.parse,
                    dont_filter=True,
                    errback=self.err_back)

    def err_back(self, failure):
        self.is_ok = False
        self.log(failure.value, 40)
        return failure.request

    def parse(self, response):
        try:
            content = json.loads(response.text)
        except:
            self.is_ok = False
            logging.info('change IP....')
            return
        if 'inbound' in content.keys():
            return
        self.is_ok = True
        li = content['outbound']
        for i in range(len(li)):
            outbound = li[i]
            num = outbound['flightCount']
            if num > 1: # 判断是否有中转
                continue
            item = FlybeItem()
            if outbound['totalHighestAdultGrossFare'] == 0:  # 该航班机票已售空
                continue
            keys = ['medium', 'high']
            price = [[0, 0]] * len(keys)
            for i, key in enumerate(keys):
                temp = outbound.get(key)
                if not temp:
                    continue
                pri = temp.get('totalAdultGrossFare') or 0
                if not pri:
                    num = 0
                else:
                    num = jsonpath(temp, '$..seatsAvailable')[0]
                price[i] = [pri, num]
            if 'low' not in outbound.keys(): # 依次查找此时的最低票价
                if 'medium' not in outbound.keys() or outbound['medium']['flights'][0]['isEligible'] is False:
                    low = outbound['high']
                else:
                    low = outbound['medium']
            else:
                low = outbound['low']

            flights = low['flights']
            departTime = outbound['departDate'][:10] + ' ' + outbound['departureTime'] + ':00'
            ti = time.mktime(time.strptime(departTime, '%Y-%m-%d %H:%M:%S'))
            row = {}
            row['depTime'] = ti
            destTime = outbound['arriveDate'][:10] + ' ' + outbound['destinationTime'] + ':00'
            ti = time.mktime(time.strptime(destTime, '%Y-%m-%d %H:%M:%S'))
            row['arrTime'] = ti
            row['depAirport'] = outbound['depart']
            row['arrAirport'] = outbound['dest']
            row['currency'] = outbound['currency']
            row['adultPrice'] = float(low['totalAdultGrossFare'])
            row['adultTax'] = float(low['totalAdultTaxes'])
            row['netFare'] = float(low['totalAdultNetFare'])
            row['maxSeats'] = flights[0]['seatsAvailable']
            row['cabin'] = flights[0]['fare']['fareClass']
            row['carrier'] = flights[0]['flightNumber'][:2]
            row['flightNumber'] = flights[0]['flightNumber']
            row['isChange'] = 1
            row['segments'] = json.dumps(price)
            row['getTime'] = time.time()
            item.update(row)
            yield item

    def get_task(self):
        input_file = open(os.path.join(r'utils/source', '%s.csv' % self.name.upper()))
        reader = csv.reader(input_file)
        datas = list(reader)
        input_file.close()
        thisday = datetime.now()
        random.shuffle(datas)
        for i in range(3, 10):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y%m%d')
            for data in datas:
                if not data or not len(data):
                    continue
                print(['%s-%s:%s:1' % (data[0], data[1], _dt)])
                yield ['%s-%s:%s:1' % (data[0], data[1], _dt)]
