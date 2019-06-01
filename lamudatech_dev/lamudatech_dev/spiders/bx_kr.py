# -*- coding: utf-8 -*-
import scrapy
import requests
# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse
from datetime import datetime, timedelta
import json, time
from jsonpath import jsonpath

from lamudatech_dev.items import FlightsItem
from lamudatech_dev.pipelines import LamudatechDevPipeline
from lamudatech_dev import settings
from utils.process_airport_city.get_airport_city import get_airport_city

class BxKrSpider(scrapy.Spider):
    name = 'b0'
    spider_name = 'b0'
    start_urls = 'https://www.airbusan.com/web/bookingApi/domesticAvail'
    version = 1.1

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection': "keep-alive",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "www.airbusan.com",
            'Origin': "https://www.airbusan.com",
            'Referer': "https://www.airbusan.com/web/individual/booking/domestic",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'X-Requested-With': "XMLHttpRequest",
            'Cache-Control': "no-cache",
        },

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        DOWNLOAD_DELAY = 0,
        # DOWNLOAD_TIMEOUT = 6,
        COOKIES_ENABLED=False,
        # LOG_FILE = 'log/%s-spider.log' % spider_name,
        # LOG_LEVEL = 'DEBUG',
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))
        while True:
            data_api = settings.GET_TASK_URL + 'carrier=B0'
            try:
                result = json.loads(requests.get(data_api, timeout=180).text).get('data')
            except Exception as e:
                self.log(e, 40)
                result = None

            if result is None:
                self.log('Date is None!\nWaiting...', 40)
                time.sleep(16)
                continue

            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')
            # _from, _to, _date = 'CJU', 'PUS', '20180923'

            # for airports in get_airports(u'釜山国内.csv'):
            #     _from = airports.get('DepartureAirportCode')
            #     _to = airports.get('ArrivalAirportCode')
            #
            #     _date = "{:%Y%m%d}".format(datetime.today())
            #
            #     _num = 31

            for _date in self._get_dates(_date, int(_num)):
                data = {
                    "bookingCategory": "Individual",
                    "foc": "N",
                    "depCity": _from,
                    "arrCity": _to,
                    "depDate": _date,
                    "bookingClass": "ES"
                }
                data_encode = parse.urlencode(data)
                yield scrapy.Request(method='POST',
                                     url=self.start_urls,
                                     body=data_encode,
                                     meta={'_from': _from, '_to': _to, '_date': _date},
                                     dont_filter=True
                                     )

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        _date = meta.get('_date')

        result = json.loads(response.text)
        # print(response.text)
        # 航班
        listFareIntAvail = jsonpath(result, '$..list.*')

        item = None

        if listFareIntAvail:
            for rec in listFareIntAvail:

                judge = rec.get('fareRate')
                if not judge:
                    continue
                # 税
                fuelAd = int(jsonpath(rec, '$..fuelAD')[0])
                taxAd = int(jsonpath(rec, '$..taxAD')[0])

                # 机场和日期
                depDate = jsonpath(rec, '$..depDate')[0]
                depCity = jsonpath(rec, '$..depCity')[0]
                arrCity = jsonpath(rec, '$..arrCity')[0]

                # 航班详情
                flightNumber = jsonpath(rec, '$..flightNo')[0]

                depTime = '%s%s' % (depDate, jsonpath(rec, '$..depTime')[0])
                arrTime = '%s%s' % (depDate, jsonpath(rec, '$..arrTime')[0])

                # 城市-机场
                from_city = self.city_airport.get(depCity, depCity)
                to_city = self.city_airport.get(arrCity, arrCity)

                bookingClass = jsonpath(rec, '$..bookingClass')[0]
                fareNet = int(jsonpath(rec, '$..fareNet')[0])
                availSeat = jsonpath(rec, '$..availSeat')[0]
                item = FlightsItem()
                item.update(dict(
                    flightNumber=flightNumber,  # 航班号
                    depTime=time.mktime(time.strptime(depTime, "%Y%m%d%H%M")).__int__(),  # 出发时间
                    arrTime=time.mktime(time.strptime(arrTime, "%Y%m%d%H%M")).__int__(),  # 达到时间
                    fromCity=from_city,  # 出发城市
                    toCity=to_city,  # 到达城市
                    depAirport=depCity,  # 出发机场
                    arrAirport=arrCity,  # 到达机场
                    currency='KRW',  # 货币种类
                    adultPrice=fareNet + taxAd + fuelAd,  # 成人票价
                    adultTax=taxAd + fuelAd,  # 税价
                    netFare=fareNet,  # 净票价
                    maxSeats=availSeat,  # 可预定座位数
                    cabin=bookingClass,  # 舱位
                    carrier=flightNumber[:2],  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="[]",  # 中转时的各个航班信息
                    getTime=time.mktime(datetime.now().timetuple()).__int__(),
                ))

                yield item

        else:
            # params = {'carrier': 'BX'}
            # data_array = []
            # data = {
            #     'fromCity': _from,
            #     'toCity': _to,
            #     'date': _date,
            # }
            # data_array.append(data)
            #
            # res = push_date(settings.PUSH_DATA_URL, params=params,
            #                 action='invalid', data_array=data_array)
            if 'EE590' in response.text:
                self.log("ip 不可用", 40)
            else:
                self.log("%s-%s:%s no flights" % (_from, _to, _date), 20)
            pass

    @staticmethod
    def _get_dates(_day, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_day, '%Y%m%d') + timedelta(day)).strftime('%Y%m%d'))
        return dates