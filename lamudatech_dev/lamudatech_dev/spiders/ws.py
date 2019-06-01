# -*- coding: utf-8 -*-
import scrapy
import json, jsonpath, time, urllib, requests, re
from datetime import datetime, timedelta
from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings
from lamudatech_dev.pipelines import LamudatechDevPipeline

from utils.process_airport_city.get_airport_city import get_airport_city
# from utils.airports_rd import get_airports
from utils.push_date import push_date


class WestjetSpider(scrapy.Spider):
    name = 'ws'
    spider_name = 'ws'
    version = 1.0

    start_urls = 'https://apiw.westjet.com/bookingservices/flightSearch?'

    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.UserAgentMiddleware': 401,
        },

        # # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        CONCURRENT_REQUESTS=4,
        CLOSESPIDER_TIMEOUT = 60*60*2,
        # DOWNLOAD_DELAY = 3,
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
        param1 = 'guests=[{"type":"adult","count":1},{"type":"child","count":0},{"type":"infant","count":0}]'
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))

        while True:
            try:
                data_api = settings.GET_TASK_URL + 'carrier=WS'
                result = json.loads(requests.get(data_api, timeout=180).text).get('data')
            except Exception as e:
                self.log(e, 40)
                result = None

            if not result:
                self.log('Date is None!', 40)
                self.log('Waiting...', 40)
                time.sleep(16)
                continue

            airports, _day, _num = result[0].split(':')
            FROM, TO = airports.split('-')
            for _day in self._get_dates(_day, int(_num)):
                param2 = '&trips=[{"order":1,"departure":"%s","arrival":"%s","departureDate":"%s"}]' % (
                FROM, TO, _day)
                total_url = self.start_urls + param1 + param2
                yield scrapy.Request(total_url,
                                     meta={'FROM': FROM, 'TO':TO, '_day': _day},
                                     callback=self.parse,
                                     dont_filter=True
                                     )

    def parse(self, response):
        meta = response.meta
        FROM = meta.get('FROM')
        TO = meta.get('TO')
        _day = meta.get('_day')

        from_city = self.city_airport.get(FROM, FROM)
        to_city = self.city_airport.get(TO, TO)

        response_dict = json.loads(response.body)

        record = jsonpath.jsonpath(response_dict, '$.flights')[0]

        item = None
        for rec in record:
            departAirportCode = jsonpath.jsonpath(rec, '$..departAirportCode')[0]
            arrivalAirportCode = jsonpath.jsonpath(rec, '$..arrivalAirportCode')[0]
            currency = jsonpath.jsonpath(rec, '$..currency')[0]

            results = jsonpath.jsonpath(rec, '$..flightOptions')[0]

            item = None
            for r in results:
                try:
                    flightSummaryStops = jsonpath.jsonpath(r, '$..flightSummaryStops')[0]
                    if flightSummaryStops == "NONSTOP":
                        flightDetails = jsonpath.jsonpath(r, '$..flightDetails')
                        priceDetails = jsonpath.jsonpath(r, '$..priceDetails')

                        flightNumber = jsonpath.jsonpath(flightDetails, '$..flightNumber')[0]
                        operatingAirline = jsonpath.jsonpath(flightDetails, '$..operatingAirline')[0]
                        departureDateRaw = jsonpath.jsonpath(flightDetails, '$..departureDateRaw')[0]
                        arrivalDateRaw = jsonpath.jsonpath(flightDetails, '$..arrivalDateRaw')[0]
                        for price in priceDetails[0]:
                            fareType = jsonpath.jsonpath(price, '$..fareType')[0]
                            totalFareAmount = float(jsonpath.jsonpath(price, '$..totalFareAmount')[0])
                            totalTaxAmount = float(jsonpath.jsonpath(price, '$..totalTaxAmount')[0])
                            try:
                                seatsAvailable = int(jsonpath.jsonpath(price, '$..seatsAvailable')[0])
                            except:
                                seatsAvailable = 6

                            if fareType == 'Econo' and operatingAirline == 'WS':
                                item = FlightsItem()
                                item.update(dict(
                                    flightNumber="WS%s"%flightNumber,  # 航班号
                                    depTime=time.mktime(time.strptime(departureDateRaw[:-4], "%Y-%m-%dT%H:%M:%S")).__int__(),  # 出发时间
                                    arrTime=time.mktime(time.strptime(arrivalDateRaw[:-4], "%Y-%m-%dT%H:%M:%S")).__int__(),  # 达到时间
                                    fromCity=from_city,  # 出发城市
                                    toCity=to_city,  # 到达城市
                                    depAirport=departAirportCode,  # 出发机场
                                    arrAirport=arrivalAirportCode,  # 到达机场
                                    currency=currency,  # 货币种类
                                    adultPrice=totalFareAmount,  # 成人票价
                                    adultTax=totalTaxAmount,  # 税价
                                    netFare=totalFareAmount - totalTaxAmount,  # 净票价
                                    maxSeats=seatsAvailable,  # 可预定座位数
                                    cabin='ECO',  # 舱位
                                    carrier='WS',  # 航空公司
                                    isChange=1,  # 是否为中转 1.直达2.中转
                                    segments="NULL",  # 中转时的各个航班信息
                                    getTime=time.mktime(datetime.now().timetuple()).__int__(),
                                ))
                                yield item
                except Exception as e:
                    self.log(e, 40)

        if item is None:
            # 设置失效
            _day = _day.replace('-', '')
            data = {'fromCity': FROM, 'toCity': TO,
                    'date': _day}
            res = push_date(settings.PUSH_DATA_URL,
                            params={'carrier': self.spider_name},
                            action='invalid', data_array=[data])
            self.log('%s-%s: %s no flights' % (FROM, TO, _day), level=20)
            pass

    @staticmethod
    def _get_dates(_day, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_day, '%Y%m%d') + timedelta(day)).strftime('%Y-%m-%d'))
        return dates