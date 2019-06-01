# -*- coding: utf-8 -*-
import scrapy, requests
# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse
from datetime import datetime, timedelta
import json, re, time

from lamudatech_dev import settings
from lamudatech_dev.items import FlightsItem
from lamudatech_dev.pipelines import LamudatechDevPipeline
from utils.push_date import push_date
from utils.process_airport_city.get_airport_city import get_airport_city
from utils.dy_process_currency.get_currency import get_currency
from utils import pubUtil
# from utils.airports_rd import get_airports


class DySpider(scrapy.Spider):
    name = 'dy'
    spider_name = 'dy'
    start_urls = 'https://www.norwegian.com/resourceipr/api/booking/availability?'
    currency_info = get_currency()
    version = 1.2

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Host': 'www.norwegian.com',
            'Proxy-Connection': 'keep-alive',
            'systeminfo': 'iOS',
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34',
            'Referer': 'https://www.norwegian.com/uk/ipr/Booking',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
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
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pubUtil.get_task(self.name, step=1)
                result = next(result_iter)
            else:
                try:
                    data_api = settings.GET_TASK_URL + 'carrier=DY'
                    result = json.loads(requests.get(data_api, timeout=180).text).get('data')
                except Exception as e:
                    self.log(e)
                    result = None

            if not result:
                self.log('Date is None!', 40)
                self.log('Waiting...', 40)
                time.sleep(16)
                continue

            airports, _day, _num = result[0].split(':')
            FROM, TO = airports.split('-')
            currency_market = self.currency_info.get(FROM)
            if currency_market:
                currencyCode = currency_market.get('currency')
                marketCode = currency_market.get('marketCode')
            else:
                currencyCode = 'EUR'
                marketCode = 'en'
            for _day in self._get_dates(_day, int(_num)):
                params = parse.urlencode(dict(
                    adultCount=3,
                    childCount=0,
                    infantCount=0,
                    # culture='en-GB',
                    currencyCode=currencyCode,
                    marketCode=marketCode,
                    origin=FROM,
                    destination=TO,
                    inboundDate=_day,
                    outboundDate=_day,
                    includeTransit='true',
                    isRoundTrip='false',
                    isSsrNeeded='false',
                ))

                total_url = self.start_urls + params
                yield scrapy.Request(total_url,
                                     meta={'FROM': FROM, 'TO': TO, '_day': _day},
                                     callback=self.parse,
                                     errback=None,
                                     dont_filter=True)

    def parse(self, response):
        meta = response.meta
        FROM = meta.get('FROM')
        TO = meta.get('TO')
        _day = meta.get('_day')

        response_json = json.loads(response.text)
        availabilityResults = response_json.get('availabilityResults')
        currency = availabilityResults.get('currency')
        routeListOutbound = availabilityResults.get('routeListOutbound')

        item = None
        for rec in routeListOutbound:
            isTransit = rec.get('isTransit')
            # 直达
            if not isTransit:
                # 航班号
                flightList = rec.get('flightList')[0]
                flightCode = flightList.get('flightCode')

                # 城市，机场
                origin = rec.get('origin')
                destination = rec.get('destination')

                depAirport= origin.get('code')
                arrAirport= destination.get('code')
                fromCity= self.city_airport.get(depAirport, depAirport)
                toCity= self.city_airport.get(arrAirport, arrAirport)

                # 时间
                departureTime = rec.get('departureTime')
                arrivalTime = rec.get('arrivalTime')

                # 价格
                price_cache = list()
                # 标准仓
                price_cache.append(rec.get('standardIdFare'))
                price_cache.append(rec.get('standardLowFare'))
                price_cache.append(rec.get('standardLowFarePlus'))
                price_cache.append(rec.get('standardFlex'))
                # 高价仓
                price_cache.append(rec.get('premiumLowFare'))
                price_cache.append(rec.get('premiumFlex'))

                # 添加套餐
                segments = []
                keys = ['standardLowFarePlus', 'standardFlex']
                for key in keys:
                    price = rec.get(key)
                    temp_price = price.get('fareValue')
                    if temp_price == 0:
                        segments.append([0, 0])
                    else:
                        segments.append([round(temp_price, 2), price.get('seatsAvailable')])

                # 过滤掉无价格的然后按价格排序
                price_cache = sorted(filter(lambda x: x.get('fareValue'), price_cache), key=lambda x: x.get('fareValue'), reverse=True)
                if price_cache:
                    fare_data = price_cache.pop()
                else:
                    fare_data = rec.get('standardLowFare')

                # 最低价，仓位，座位
                fareValue = fare_data.get('fareValue')
                cabin = fare_data.get('bookingClass', 'E')
                seatsAvailable = fare_data.get('seatsAvailable')

                item = FlightsItem()
                item.update(dict(
                    flightNumber=flightCode,  # 航班号
                    depTime=time.mktime(time.strptime(departureTime, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 出发时间 "2018-04-02T06:15:00"
                    arrTime=time.mktime(time.strptime(arrivalTime, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 达到时间
                    fromCity=fromCity,  # 出发城市
                    toCity=toCity,  # 到达城市
                    depAirport=depAirport,  # 出发机场
                    arrAirport=arrAirport,  # 到达机场
                    currency=currency,  # 货币种类
                    adultPrice=float(fareValue),  # 成人票价
                    adultTax=0,  # 税价
                    netFare=float(fareValue),  # 净票价
                    maxSeats=seatsAvailable,  # 可预定座位数
                    cabin=cabin,  # 舱位
                    carrier=flightCode[:2],  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments=json.dumps(segments),  # 中转时的各个航班信息
                    getTime=time.time().__int__(),
                ))
                yield item

        if item is None:
            # 设置失效
            _day = _day.replace('-', '')
            data = {'fromCity': FROM, 'toCity': TO,
                    'date': _day}
            res = push_date(self.settings.get('PUSH_DATA_URL'),
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