# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta

# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings

from utils.process_airport_city.get_airport_city import get_airport_city

from utils.airports_rd import get_airports
from utils.push_date import push_date


class A5jSpider(scrapy.Spider):
    name = 'a5j'
    spider_name = 'dg'
    start_urls = 'https://cebmobileapi.azure-api.net/dotrez-prod/api/nsk/v1/availability/search'
    header_key = '6502d15189834519a00165162734e729'
    err_429 = False
    version = 1.0
    admin_fees = {'MNLCGY': '224.00 ', 'MNLPEK': '250.00 ', 'MNLDVO': '224.00 ', 'TPECEB': '250.00 ', 'HKGCEB': '0.00 ', 'TPEMNL': '250.00 ', 'MNLCAN': '250.00 ', 'CEBMNL': '224.00 ', 'SINCEB': '11.00 ', 'MNLKUL': '250.00 ', 'MNLPVG': '250.00 ', 'MFMMNL': '60.00 ', 'CGYMNL': '224.00 ', 'PEKMNL': '55.00 ', 'MNLCEB': '224.00 ', 'DGTMNL': '224.00 ', 'NRTCEB': '900.00 ', 'CEBTPE': '250.00 ', 'CRKMFM': '250.00 ', 'MNLNRT': '250.00 ', 'CEBHKG': '250.00 ', 'ICNMNL': '9000.00 ', 'MNLBKI': '300.00 ', 'MNLMPH': '224.00 ', 'LGPMNL': '224.00 ', 'TAGMNL': '224.00 ', 'MNLSIN': '250.00 ', 'HKGMNL': '0.00 ', 'PVGMNL': '55.00 ', 'MNLXMN': '250.00 ', 'MFMCRK': '60.00 ', 'KLOICN': '250.00 ', 'NGOMNL': '900.00 ', 'MNLNGO': '250.00 ', 'ICNKLO': '9000.00 ', 'MNLICN': '250.00 ', 'CEBICN': '250.00 ', 'NRTMNL': '900.00 ', 'CEBNRT': '250.00 ', 'KULMNL': '30.00 ', 'CANMNL': '55.00 ', 'MNLHKG': '250.00 ', 'HKGCRK': '0.00 ', 'SINMNL': '11.00 ', 'XMNMNL': '55.00 ', 'MNLMFM': '250.00 ', 'MNLSYD': '300.00 ', 'BKKMNL': '280.00 ', 'CEBSIN': '250.00 ', 'MNLTAG': '224.00 ', 'MPHMNL': '224.00 ', 'SGNMNL': '8.00 ', 'MNLDGT': '224.00 '}

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Host': "cebmobileapi.azure-api.net",
            # 'loggly-tracking-id': "630070",
            'Accept': "application/json",
            # 'Authorization': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJkb3RSRVogQVBJIiwianRpIjoiYjgzZTYwYmItNmNhZi00NDZlLTRkNzgtYzIxZDMyMDUzMjkxIiwiaXNzIjoiQVBJIn0.4KG4Vbc6hnTFTFt9lwleVJFkVzmqtSv94trtuqk6Ux0",
            'Proxy-Connection': "keep-alive",
            'Accept-Language': "zh-cn",
            'Accept-Encoding': "gzip,deflate",
            'Content-Type': "application/json; charset=utf-8",
            # 'User-Agent': "Cebu%20Pacific/40467 CFNetwork/758.5.3 Darwin/15.6.0",
            'User-Agent': "Cebu%20Pacific/41137 CFNetwork/758.5.3 Darwin/15.6.0",
            'ocp-apim-subscription-key': header_key,
            'Connection': "keep-alive",
            # 'Authorization-Secret': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBuYW1lIjoiY2VidXBhY2lmaWMiLCJ2ZXJzaW9uIjoiMi4xMS4wIiwibG9nZ2x5SWQiOiI2MzAwNzAifQ.Vq5qOSwm8IHW9jNjvmPZgLHaeUAwX-UXfhBK48mqqos",
            # 'Cookie': "dotrez=2417091594.47873.0000",
            'Cache-Control': "no-cache"
        },

        # 仅供测试用
        ITEM_PIPELINES={
            'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        },

        DOWNLOADER_MIDDLEWARES={
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.A5jProcessCookies': 300,
        },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        # DOWNLOAD_DELAY=3,
        # DOWNLOAD_TIMEOUT=6,
        # COOKIES_ENABLED=False,
        HTTPERROR_ALLOWED_CODES=[429, 404, 500],
        # LOG_FILE = 'log/%s-spider.log' % spider_name,
        # LOG_LEVEL = 'DEBUG',
        )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        while True:
            result = self.get_task(self.spider_name)
            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')
            for _date in self._get_dates(_date, int(_num)):
                # s = '{"Passengers":{"Types":[{"Type":"ADT","Count":1}]},"Criteria":[{"Filters":{"IncludeAllotments":false,"Filter":"ExcludeDeparted","ProductClasses":[]},"Stations":{"DestinationStationCodes":["SIN"],"OriginStationCodes":["MNL"],"SearchDestinationMacs":false,"SearchOriginMacs":false},"Dates":{"BeginDate":"2018-06-27T00:00:00","EndDate":"2018-06-27T00:00:00"},"FlightFilters":{"Type":5,"MaxConnectingFlights":20}}],"Codes":{"Currency":"PHP"},"FareFilters":{"ClassControl":"Default","MaxPrice":0.0,"MinPrice":0.0,"Loyalty":0,"Classes":["Y","U","S","B","H","M","K","L","Q","G","W","V","C","D","E","Z","PA","PD","A","P"]},"TaxesAndFees":"TaxesAndFees"}'
                payload = {
                    "Passengers":{"Types":[{"Type":"ADT","Count":1}]},
                    "Criteria":[{"Filters":{"IncludeAllotments":False,"Filter":"ExcludeDeparted","ProductClasses":[]},
                                 "Stations":{"DestinationStationCodes":[_to],"OriginStationCodes":[_from],"SearchDestinationMacs":False,"SearchOriginMacs":False},
                                 "Dates":{"BeginDate":"%sT00:00:00"%_date,"EndDate":"%sT00:00:00"%_date},"FlightFilters":{"Type":5,"MaxConnectingFlights":20}}],
                    # "Codes":{"Currency":"PHP"},
                    "FareFilters":{"ClassControl":"Default","MaxPrice":0.0,"MinPrice":0.0,"Loyalty":0,"Classes":["Y","U","S","B","H","M","K","L","Q","G","W","V","C","D","E","Z","PA","PD","A","P"]},
                    "TaxesAndFees":"TaxesAndFees"
                }
                body = json.dumps(payload)
                yield scrapy.Request(self.start_urls, method='POST', body=body,
                                     meta={'_from': _from, '_to': _to, '_date': _date})

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        _date = meta.get('_date')

        if response.status == 404:
            # data=null
            self.log('404, No flights on this day: %s-%s[%s]' % (_from, _to , _date), 20)
            return
        elif response.status == 500:
            self.log(response.text, 40)
            return

        data_map = json.loads(response.text).get('data')
        trips = data_map.get('trips')
        if not trips:
            # 当天无航班
            pass
        else:
            # 货币种类
            currencyCode = data_map.get('currencyCode')

            faresAvailable = data_map.get('faresAvailable')
            for trip in trips:
                journeysAvailable = trip['journeysAvailable']
                for journey in journeysAvailable:
                    if journey['stops'] == 0:
                        segments = journey['segments'][0]
                        designator = segments['designator']
                        # 机场，时间
                        dep_airport = designator['origin']
                        arr_airport = designator['destination']
                        dep_date = designator['departure']
                        arr_date = designator['arrival']

                        from_city = self.city_airport.get(dep_airport, dep_airport)
                        to_city = self.city_airport.get(arr_airport, arr_airport)

                        # 航班号，航司
                        identifier = segments['identifier']
                        flight_number = identifier['identifier']
                        carrierCode = identifier['carrierCode']

                        items = []
                        fares = journey['fares']
                        for fare_key, fare_value in fares.items():
                            # 座位
                            availableCount = fare_value['availableCount']
                            # 仓位
                            classOfService = fare_value['classOfService']
                            fare_rec = faresAvailable[fare_key]
                            passengerFares = fare_rec['passengerFares'][0]
                            # 纯价格
                            serviceCharges = float(passengerFares['serviceCharges'][0]['amount'])
                            # 总价
                            fareAmount = float(passengerFares['fareAmount'])

                            # 管理费
                            admin_fees = self.admin_fees.get(dep_airport+arr_airport)
                            if admin_fees is None:
                                self.log('new flight line, no found admin fees', 40)
                            else:
                                admin_fees = float(admin_fees)

                                item = FlightsItem()
                                item.update(dict(
                                    flightNumber=carrierCode+flight_number,  # 航班号
                                    depTime=time.mktime(time.strptime(dep_date, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 出发时间
                                    arrTime=time.mktime(time.strptime(arr_date, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 达到时间
                                    fromCity=from_city,  # 出发城市
                                    toCity=to_city,  # 到达城市
                                    depAirport=dep_airport,  # 出发机场
                                    arrAirport=arr_airport,  # 到达机场
                                    currency=currencyCode,  # 货币种类
                                    adultPrice=fareAmount+admin_fees,  # 成人票价
                                    adultTax=admin_fees,  # 税价
                                    netFare=fareAmount,  # 净票价
                                    maxSeats=availableCount,  # 可预定座位数
                                    cabin=classOfService,  # 舱位
                                    carrier=carrierCode,  # 航空公司
                                    isChange=1,  # 是否为中转 1.直达2.中转
                                    segments="NULL",  # 中转时的各个航班信息
                                    getTime=int(time.time()),
                                ))
                                items.append(item)

                        if not fares:
                            item = FlightsItem()
                            item.update(dict(
                                flightNumber=carrierCode + flight_number,  # 航班号
                                depTime=time.mktime(time.strptime(dep_date, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 出发时间
                                arrTime=time.mktime(time.strptime(arr_date, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 达到时间
                                fromCity=from_city,  # 出发城市
                                toCity=to_city,  # 到达城市
                                depAirport=dep_airport,  # 出发机场
                                arrAirport=arr_airport,  # 到达机场
                                currency=currencyCode,  # 货币种类
                                adultPrice=0,  # 成人票价
                                adultTax=0,  # 税价
                                netFare=0,  # 净票价
                                maxSeats=0,  # 可预定座位数
                                cabin='',  # 舱位
                                carrier=carrierCode,  # 航空公司
                                isChange=1,  # 是否为中转 1.直达2.中转
                                segments="[]",  # 中转时的各个航班信息
                                getTime=int(time.time()),
                            ))
                            yield item
                            continue

                        yield min(items, key=lambda item: item['adultPrice'])

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_date, '%Y%m%d') + timedelta(day)).strftime('%Y-%m-%d'))
        return dates

    def get_task(self, carrier):
        task_api = settings.GET_TASK_URL + 'carrier=%s' % carrier
        try:
            result = json.loads(requests.get(task_api, timeout=180).text).get('data')
        except Exception as e:
            self.log(e, 40)
            result = None
        if not result:
            self.log('Date is None!\nWaiting...', 40)
            time.sleep(16)
        return result
