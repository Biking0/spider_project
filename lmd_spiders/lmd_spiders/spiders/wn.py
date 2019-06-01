# -*- coding: utf-8 -*-
import scrapy, os, csv, logging
from datetime import datetime, timedelta
import urllib as parse
from lmd_spiders import settings
from utils import dataUtil, pubUtil
from utils.spe_util import vyUtil
import json, time
from jsonpath import jsonpath
from lmd_spiders.items import LmdSpidersItem


class WnSpider(scrapy.Spider):
    name = 'wn'
    allowed_domains = ['mobile.southwest.com']
    start_urls = 'https://mobile.southwest.com/api/mobile-air-booking/v1/mobile-air-booking/page/flights/products?'
    carrier = 'WN'
    task = []
    version = 1.8
    isOK = False

    custom_settings = dict(

        DEFAULT_REQUEST_HEADERS={
            "Host": "mobile.southwest.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:61.0) Gecko/20100101 Firefox/61.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://mobile.southwest.com/air/booking/shopping/adult/outbound/results",
            "X-API-Key": "l7xx0a43088fe6254712b10787646d1b298e",
            "X-Channel-ID": "MWEB",
            "X-User-Experience-ID": "a3a5bae8-f65e-4de0-a7d8-710cf4cb45bc",
            "X-Requested-With": "XMLHttpRequest",
            "Connection": "keep-alive",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        },

        SEAT_SEARCH=3,

        CONCURRENT_REQUESTS=16,

        NOT_USE_SELF=True,

        PROXY_TRY_NUM=3,

        # DOWNLOAD_DELAY = 5,

        # ITEM_PIPELINES={  # 往测试库添加数据
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },

        DOWNLOADER_MIDDLEWARES={
            'lmd_spiders.middlewares.StatisticsItem': 200,
            'lmd_spiders.middlewares.ProxyMiddleware': 300,
        },

    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pubUtil.get_task(self.name)
                result = next(result_iter)
            else:
                result = pubUtil.getUrl(self.carrier, 1)
            if not result:
                time.sleep(3)
                continue
            for data in result:
                (dt_st, dep, arr, days) = vyUtil.analysisData(data) 
                for i in range(int(days)):
                    dt = vyUtil.get_real_date(dt_st, i)
                    params = {
                        'origination-airport': dep,
                        'destination-airport': arr,
                        'departure-date': dt,
                        'number-adult-passengers': self.custom_settings.get('SEAT_SEARCH'),
                        'number-senior-passengers': 0,
                        'currency': 'USD',
                    }
                    total_url = self.start_urls + parse.urlencode(params)
                    yield scrapy.Request(
                        url=total_url,
                        method="GET",
                        dont_filter=True,
                        callback=self.parse,
                        errback=self.errback,
                    )

    def errback(self, failure):
        self.log(failure.value, 40)
        self.isOK = False
        return failure.request

    def parse(self, response):
        try:
            content = json.loads(response.body)
        except Exception as e:
            self.log(e, 20)
            self.isOK = False
            return
        self.isOK = True
        try:
            dep, arr = jsonpath(content, '$..airportInfo')[0].replace(' ', '').split('-')
        except:
            if content.get('code') == 400521204:
                self.log('error_no_routes_exists', 20)
                print(content.get('infoList'))
                return
        date = jsonpath(content, '$..selectedDate')
        date = date[0]
        flights = jsonpath(content, '$..cards')[0]
        for flight in flights:
            if jsonpath(flight, '$..numberOfStops')[0]:
                continue
            flightNumber = self.carrier + flight.get('flightNumbers')
            dep_time_str = '%s %s:00' % (date, flight.get('departureTime'))  # 字符串格式的出发时间
            arr_time_str = '%s %s:00' % (date, flight.get('arrivalTime'))  # 字符串格式的到达时间
            dep_time = time.mktime(time.strptime(dep_time_str, '%Y-%m-%d %H:%M:%S'))
            arr_time = time.mktime(time.strptime(arr_time_str, '%Y-%m-%d %H:%M:%S'))
            _fare = flight.get('fares')
            product_id = ''
            keys = ['Anytime']
            seg = [[0, 0]]
            if not _fare:
                netfare = 0
                seat = 0
                currency = 'USD'
            else:
                price = None
                for fare in _fare:
                    if fare.get('reasonIfUnavailable'):
                        continue
                    key = fare.get('fareDescription')
                    if key in keys:
                        index = keys.index(key)
                        flag_netfare = float(jsonpath(fare, '$..amount')[0])
                        seat_str = fare.get('limitedSeats')
                        flag_seat = 9 if not seat_str else int(seat_str.split(' ')[0])
                        flag_product_id = jsonpath(fare, '$..productId')[0]
                        seg[index] = [flag_netfare, flag_seat, flag_product_id]
                    if not price:
                        price = fare
                netfare = float(jsonpath(price, '$..amount')[0])
                currency = jsonpath(price, '$..currencyCode')[0]
                seat_str = price.get('limitedSeats')
                product_id = jsonpath(price, '$..productId')[0]
                seat = 9 if not seat_str else int(seat_str.split(' ')[0])
            item = LmdSpidersItem()
            item.update(dict(
                flightNumber=flightNumber,
                depAirport=dep,
                arrAirport=arr,
                carrier=self.carrier,
                depTime=dep_time,
                arrTime=arr_time,
                currency=currency,
                segments=json.dumps(seg),
                isChange=1,
                getTime=time.time(),
                fromCity=self.portCitys.get(dep, dep),
                toCity=self.portCitys.get(arr, arr),
                cabin='W',
                adultPrice=netfare,
                netFare=netfare,
                adultTax=0,
                maxSeats=seat,
                info=product_id
            ))
            yield item

    def get_task(self):
        inputFile = open(os.path.join('utils', 'WN.csv'))
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now()
        #倒序输出
        for i in range(3,10):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y-%m-%d')
            for data in datas:
                if not data or not len(data):
                    continue
                yield (data[0], data[1], _dt)