# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta
from jsonpath import jsonpath
# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings
from lamudatech_dev.pipelines import LamudatechDevPipeline

from utils.process_airport_city.get_airport_city import get_airport_city

# from utils.airports_rd import get_airports
from utils.push_date import push_date


class LjSpider(scrapy.Spider):
    name = 'lj'
    spider_name = 'lj'
    start_urls = 'https://www.jinair.com/booking/getAirAvailabilityJson'
    version = 1.0

    change_cookies = False

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'accept': "application/json, text/javascript, */*; q=0.01",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'content-type': "application/json; charset=UTF-8",
            'origin': "https://www.jinair.com",
            'referer': "https://www.jinair.com/booking/getAvailabilityList",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'x-requested-with': "XMLHttpRequest",
            'Cache-Control': "no-cache"
        },

        DOWNLOADER_MIDDLEWARES={
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.LjProcessCookies': 500,
        },

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        # DOWNLOAD_DELAY=3,
        RETRY_ENABLED=False,
        # DOWNLOAD_TIMEOUT = 6,
        # COOKIES_ENABLED=True,
        HTTPERROR_ALLOWED_CODES=[403, 500],
        # LOG_FILE='log/%s-spider.log' % spider_name,
        # LOG_LEVEL='DEBUG',
        )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins))
        while True:
            result = self.get_task(self.spider_name)
            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')

            for _date in self._get_dates(_date, int(_num)):
                data = {"searchType": "", "origin1": _from, "destination1": _to, "travelDate1": _date,
                        "origin2": "", "destination2": "", "travelDate2": "", "origin3": "", "destination3": "",
                        "travelDate3": "", "origin4": "", "destination4": "", "travelDate4": "", "pointOfPurchase": "",
                        "adultPaxCount": "1", "childPaxCount": "0", "infantPaxCount": "0", "tripType": "OW", "cpnNo": "",
                        "promoCode": "", "refVal": "JINAIR", "refPop": "", "refChannel": "", "refLang": ""}

                yield scrapy.Request(self.start_urls, method='POST',
                                     meta={'_from': _from, '_to': _to, '_date': _date},
                                     body=json.dumps(data),
                                     dont_filter=True)
            else:
                self.change_cookies = True

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        _date = meta.get('_date')

        if response.status == 500:
            self.log((_from, _to, _date), 20)
            self.log(response.text, 20)

            # 设置失效
            data = {'fromCity': _from, 'toCity': _to, 'date': _date}
            push_date(settings.PUSH_DATA_URL,
                      params={'carrier': self.spider_name},
                      action='invalid', data_array=[data])

        else:
            response_dict = json.loads(response.text)
            tripInfo = jsonpath(response_dict, '$..tripInfo.*')
            if not tripInfo:
                # 设置失效
                data = {'fromCity': _from, 'toCity': _to, 'date': _date}
                push_date(settings.PUSH_DATA_URL,
                          params={'carrier': self.spider_name},
                          action='invalid', data_array=[data])
            else:
                item = None
                for rec in tripInfo:
                    segmentInfo_list = rec['segmentInfo']
                    if len(segmentInfo_list) == 1:
                        segmentInfo = segmentInfo_list[0]
                        carrierCode = jsonpath(segmentInfo, '$.flightIdentifierInfo.carrierCode')[0]
                        flightNumber = jsonpath(segmentInfo, '$.flightIdentifierInfo.flightNumber')[0]

                        dep_airport = jsonpath(segmentInfo, '$.departureInfo.airportCode')[0]
                        departureDateTime = jsonpath(segmentInfo, '$.departureDateTime')[0]
                        dep_date = ''.join(re.match(r'(.*)\(.*\)(.*)', departureDateTime).groups())

                        arr_airport = jsonpath(segmentInfo, '$.arrivalInfo.airportCode')[0]
                        arrivalDateTime = jsonpath(segmentInfo, '$.arrivalDateTime')[0]
                        arr_date = ''.join(re.match(r'(.*)\(.*\)(.*)', arrivalDateTime).groups())

                        # 城市
                        fromCity = self.city_airport.get(dep_airport, dep_airport)
                        toCity = self.city_airport.get(arr_airport, arr_airport)

                        # 价格
                        segmentAvailability = segmentInfo['segmentAvailability']

                        # 比价
                        items = []
                        for rec_price in segmentAvailability:
                            bookingClass = rec_price['bookingClass']
                            # 跳过没有数据的仓位
                            if not bookingClass:
                                continue
                            seatAvailablity = rec_price['seatAvailablity']
                            displayFareAmount = rec_price['displayFareAmount']
                            taxAmount = rec_price['taxAmount']
                            displayFareCurrencyCode = rec_price['displayFareCurrencyCode']

                            item = FlightsItem()
                            item.update(dict(
                                flightNumber='%s%s'%(carrierCode, flightNumber),  # 航班号
                                depTime=int(time.mktime(time.strptime(dep_date, '%Y-%m-%d %H:%M'))),  # 出发时间
                                arrTime=int(time.mktime(time.strptime(arr_date, '%Y-%m-%d %H:%M'))),  # 达到时间
                                fromCity=fromCity,  # 出发城市
                                toCity=toCity,  # 到达城市
                                depAirport=dep_airport,  # 出发机场
                                arrAirport=arr_airport,  # 到达机场
                                currency=displayFareCurrencyCode,  # 货币种类
                                adultPrice=displayFareAmount+taxAmount,  # 成人票价
                                adultTax=taxAmount,  # 税价
                                netFare=displayFareAmount,  # 净票价
                                maxSeats=seatAvailablity,  # 可预定座位数
                                cabin=bookingClass,  # 舱位
                                carrier=carrierCode,  # 航空公司
                                isChange=1,  # 是否为中转 1.直达2.中转
                                segments="NULL",  # 中转时的各个航班信息
                                getTime=int(time.time()),
                            ))
                            items.append(item)

                        # 比价，座位小于3个的不要
                        gt_2_items = filter(lambda x: x['maxSeats'] > 2, items)
                        if gt_2_items:
                            yield min(gt_2_items, key=lambda x: x['adultPrice'])
                        else:
                            yield min(items, key=lambda x: x['adultPrice'])

                    else:
                        print(_from, _to, _date)
                        print('is_change')
                        break

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_date, '%Y%m%d') + timedelta(day)).strftime('%Y%m%d'))
        return dates

    def get_task(self, carrier):
        task_api = settings.GET_TASK_URL + 'carrier=%s' % carrier
        while True:
            try:
                result = json.loads(requests.get(task_api, timeout=180).text).get('data')
            except Exception as e:
                self.log(e, 40)
                result = None
            if not result:
                self.log('Date is None!\nWaiting...', 40)
                time.sleep(16)
                continue
            return result
