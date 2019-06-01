# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta
from itertools import groupby
# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings
from lamudatech_dev.pipelines import LamudatechDevPipeline

from utils.process_airport_city.get_airport_city import get_airport_city

from utils.push_date import push_date


class SnSpider(scrapy.Spider):
    name = 'sn'
    spider_name = 'sn'
    start_urls = 'https://www.brusselsairlines.com/'
    version = 1.0

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Host': "services.brusselsairlines.com",
            'Connection': "keep-alive",
            'Proxy-Connection': "keep-alive",
            'Accept': "*/*",
            'User-Agent': "Brussels%20Airlines/2620 CFNetwork/758.5.3 Darwin/15.6.0",
            'Accept-Language': "en-us",
            'Authorization': "Basic U2VudGlCQV9CbW9iOkRsU21sb3QxMTA=",
            'Accept-Encoding': "gzip, deflate",
            'Cache-Control': "no-cache",
            },

            # 仅供测试用
            # ITEM_PIPELINES={
            #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
            # },

            CONCURRENT_REQUESTS=4,
            CLOSESPIDER_TIMEOUT=60 * 60 * 2,
            # DOWNLOAD_DELAY = 3,
            # DOWNLOAD_TIMEOUT = 6,
            # COOKIES_ENABLED=False,
            # HTTPERROR_ALLOWED_CODES=[403],
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
            data_api = settings.GET_TASK_URL + 'carrier=%s' % self.spider_name
            try:
                result = json.loads(requests.get(data_api, timeout=180).text).get('data')
            except Exception as e:
                self.log(e, 40)
                result = None

            if not result:
                self.log('Date is None!\nWaiting...', 40)
                time.sleep(16)
                continue

            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')

            _date = re.sub(r'(\d{4})(\d{2})(\d{2})', r'\1-\2-\3', _date)

            for _date in self._get_dates(_date, int(_num)):
                base_url = 'https://services.brusselsairlines.com/Services/BMobileREST.svc/WebHttpsEndpoint/api/search-low-fare-trips?'

                params = {
                        'cabin': 'Economy',
                        'flexible': 'false',
                        'leg': 'index:0;origin:{_from};originType:A;destination:{_to};destinationType:A;date:{_date}'.format(
                            _from=_from, _to=_to, _date=_date
                            ),
                        'ln': 'en',
                        'pos': 'BEL_REST',
                        'traveler': 'code:ADT'
                }

                total_url = base_url + parse.urlencode(params)
                yield scrapy.Request(total_url,
                                     meta={'_from': _from, '_to': _to, '_date': _date},
                                     dont_filter=True)

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        _date = meta.get('_date')

        results = json.loads(response.text).get('AirLowFareSearchRS')

        # 设置失效
        if results is None:
            params = {'carrier': self.spider_name}

            data_array = list()
            data = {
                'fromCity': _from,
                'toCity': _to,
                'date': re.sub(r'(\d+)-(\d+)-(\d+)', r'\1\2\3', _date),
            }
            data_array.append(data)
            res = push_date(settings.PUSH_DATA_URL, params=params,
                            action='invalid', data_array=data_array)
            self.log('%s-%s: %s no flights' % (_from, _to, _date), level=20)
            return

        item = None
        items = []
        # 航班信息
        FlightInformation = results['FlightInformationSummary']['FlightInformation']
        flight_info_list = [flight for flight in FlightInformation if _date in flight['Flight'][0]['FlightSegment'][0]['@DepartureDate']]
        for flight_info in flight_info_list:
            if len(flight_info['Flight'][0]['FlightSegment']) == 1:
                info_rec = flight_info['Flight'][0]['FlightSegment'][0]
                flight_id = info_rec['@ID']
                flightNumber = info_rec['@FlightNumber']
                dep_data = info_rec['@DepartureDate'][:19]
                arr_date = info_rec['@ArrivalDate'][:19]
                depAirport = info_rec['@OriginCode']
                arrAirport = info_rec['@DestinationCode']
                carrier = info_rec['@MarketingAirline']
                fromCity = self.city_airport.get(depAirport, depAirport)
                toCity = self.city_airport.get(arrAirport, arrAirport)

                # 座位信息
                FlightItineraryPricePoint = results['FlightItineraryPricePoints']['FlightItineraryPricePoint']
                for seat_info in FlightItineraryPricePoint:
                    # 价格point
                    PricePointRef = seat_info['PricePointRef']
                    FlightInformationAttributes = seat_info['FlightInformationAttributes'][0]
                    if flight_id == FlightInformationAttributes['@FlightSegmentRef']:
                        cabin = FlightInformationAttributes['@BookingClass']
                        maxSeats = FlightInformationAttributes['@SeatsAvailable']

                        # 价格信息
                        PricePoint = results['PricePointSummary']['PricePoint']
                        for price_info in PricePoint:
                            if PricePointRef == price_info['@ID']:
                                Fare = price_info['BasedOnPTCPricing']['Fare']
                                netFare = float(Fare['@BaseFareAmount'])
                                BaseFareCurrency = Fare['@BaseFareCurrency']
                                TotalFareAmount = float(Fare['@TotalFareAmount'])

                                item = FlightsItem()
                                item.update(dict(
                                    flightNumber=carrier+flightNumber,  # 航班号
                                    depTime=int(time.mktime(time.strptime(dep_data, "%Y-%m-%dT%H:%M:%S"))),  # 出发时间
                                    arrTime=int(time.mktime(time.strptime(arr_date, "%Y-%m-%dT%H:%M:%S"))),  # 达到时间
                                    fromCity=fromCity,  # 出发城市
                                    toCity=toCity,  # 到达城市
                                    depAirport=depAirport,  # 出发机场
                                    arrAirport=arrAirport,  # 到达机场
                                    currency=BaseFareCurrency,  # 货币种类
                                    adultPrice=TotalFareAmount,  # 成人票价
                                    adultTax=TotalFareAmount-netFare,  # 税价
                                    netFare=netFare,  # 净票价
                                    maxSeats=maxSeats,  # 可预定座位数
                                    cabin=cabin,  # 舱位
                                    carrier=carrier,  # 航空公司
                                    isChange=1,  # 是否为中转 1.直达2.中转
                                    segments="NULL",  # 中转时的各个航班信息
                                    getTime=int(time.time()),
                                ))
                                # 比价
                                items.append(item)

        # 按航班号分组，返回最低价
        items = sorted(items, key=lambda x: x['flightNumber'])
        items_group = groupby(items, key=lambda x: x['flightNumber'])
        for k, g in items_group:
            yield min(g, key=lambda x: x['adultPrice'])

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_date, '%Y-%m-%d') + timedelta(day)).strftime('%Y-%m-%d'))
        return dates
