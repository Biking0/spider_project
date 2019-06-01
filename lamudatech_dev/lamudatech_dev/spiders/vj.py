# -*- coding: utf-8 -*-
import json, time, logging, traceback
from datetime import datetime, timedelta
import jsonpath, re
import scrapy
import requests

from lamudatech_dev.items import FlightsItem
from lamudatech_dev.pipelines import LamudatechDevPipeline
from utils.process_airport_city.get_airport_city import get_airport_city

from lamudatech_dev import settings
from utils import pubUtil


class VjSpider(scrapy.Spider):
    name = 'vj'
    spider_name = 'vj'
    start_urls = 'https://mapi.vietjetair.com/apiios/get-flight2.php'
    version = 1.3
    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'accept': "application/json, text/javascript, */*; q=0.01",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
            'origin': "https://m.vietjetair.com",
            'referer': "https://m.vietjetair.com/",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'Cache-Control': "no-cache"
        },
        CONCURRENT_REQUESTS=4,
        # DOWNLOAD_DELAY=3,
        DOWNLOAD_TIMEOUT=15,

        HTTPERROR_ALLOWED_CODES=[403, 504],

        DOWNLOADER_MIDDLEWARES={
            'lamudatech_dev.middlewares.StatisticsItem': 300,
            'lamudatech_dev.middlewares.VjProxyMiddleware': 400,

        },

        COOKIES_ENABLED=False,

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        # LOG_FILE='log/{}-spider.log'.format(spider_name),
        # LOG_LEVEL='DEBUG'
    )
    is_ok = True

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
                    result_iter = pubUtil.get_task(self.name, step=7, st=2)
                result = next(result_iter)
            else:
                try:
                    data_api = settings.GET_TASK_URL + 'carrier=VJ'
                    result = json.loads(requests.get(data_api, timeout=180).text).get('data')
                except Exception as e:
                    self.log(e)
                    result = None
            if not result:
                logging.info('Date is None!')
                logging.info('Waiting...')
                continue
            airports, _day, _num = result[0].split(':')
            FROM, TO = airports.split('-')

            _day = re.sub(r'(\d{4})(\d{2})(\d{2})', r'\1-\2-\3', _day)

            # for airports in get_airports(u'越捷航空.csv'):
            #     FROM = airports.get('DepartureAirportCode')
            #     TO = airports.get('ArrivalAirportCode')
            #
            #     _day = "{:%Y-%m-%d}".format(datetime.today())

            for _day in self._get_dates(_day, int(_num)):
                    data = {
                        'OutboundDate': _day,
                        'DaysBefore': '0',
                        'DaysAfter': '0',
                        'AdultCount': '1',
                        'ChildCount': '0',
                        'InfantCount': '0',
                        'DepartureAirportCode': FROM,
                        'ArrivalAirportCode': TO,
                        'CurrencyCode': 'VND',
                        'PromoCode': ''
                    }
                    yield scrapy.FormRequest(self.start_urls,
                                             formdata=data,
                                             meta={'FROM': FROM, 'TO': TO},
                                             callback=self.parse,
                                             dont_filter=True,
                                             # errback=lambda x: self.download_errback(x, FROM, TO)
                                             errback=self.errback,
                                             )

    def errback(self, failure):
        logging.info(failure.value)
        # time.sleep(8)
        self.is_ok = False
        return failure.request

    # def download_errback(self, x, FROM, TO):
    #     logging.info('error download:' + FROM + ':' + TO)
    #     self.is_ok = False

    def parse(self, response):
        meta = response.meta
        logging.debug('proxy: %s' % meta.get('proxy'))
        # print(response.body)
        item = FlightsItem()
        try:
            response_dict = json.loads(response.body)
            self.is_ok = True
            results = jsonpath.jsonpath(response_dict, '$..OutboundOptions.Option')
            LegOption = jsonpath.jsonpath(results, '$..LegOption')
            DepartureDate = jsonpath.jsonpath(results, '$..DepartureDate')
            if DepartureDate and DepartureDate[0]:
                for result in LegOption:
                    SegmentOptions = jsonpath.jsonpath(result, '$..SegmentOptions')[0]

                    segmentOption = SegmentOptions.get('SegmentOption')
                    if isinstance(segmentOption, list):
                        continue
                    Surcharge = jsonpath.jsonpath(result, '$.Surcharges.Surcharge')
                    Total = jsonpath.jsonpath(Surcharge, '$..Total')
                    if Total:
                        Total = sum(Total)
                    else:
                        Total = 0
                    Flight = jsonpath.jsonpath(SegmentOptions, '$..Flight')
                    flightNumber = jsonpath.jsonpath(Flight, '$..Number')[0]
                    depTime = jsonpath.jsonpath(Flight, '$..ETDLocal')[0]
                    arrTime = jsonpath.jsonpath(Flight, '$..ETALocal')[0]
                    DepartureAirport = jsonpath.jsonpath(Flight, '$..DepartureAirport.Code')[0]
                    ArrivalAirport = jsonpath.jsonpath(Flight, '$..ArrivalAirport.Code')[0]

                    FareOption = jsonpath.jsonpath(result, '$..FareOption.*')

                    from_city = self.city_airport.get(DepartureAirport, DepartureAirport)
                    to_city = self.city_airport.get(ArrivalAirport, ArrivalAirport)
                    # 缓存最低价
                    item_cache = None
                    for rec in FareOption:
                        DiscountFare = jsonpath.jsonpath(rec, '$..DiscountFare')[0]
                        DiscountFareTaxes = jsonpath.jsonpath(rec, '$..DiscountFareTaxes')[0]
                        DiscountFareTotal = jsonpath.jsonpath(rec, '$..DiscountFareTotal')[0]
                        Abbreviation = jsonpath.jsonpath(rec, '$..Currency.Abbreviation')[0]
                        SeatsAvailable = jsonpath.jsonpath(rec, '$..SeatsAvailable')[0]
                        FareCategory = jsonpath.jsonpath(rec, '$..FareCategory')[0]

                        item.update(dict(
                            flightNumber=flightNumber,  # 航班号
                            depTime=time.mktime(time.strptime(depTime, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 出发时间
                            arrTime=time.mktime(time.strptime(arrTime, "%Y-%m-%dT%H:%M:%S")).__int__(),  # 达到时间
                            fromCity=from_city , # 出发城市
                            toCity=to_city, # 到达城市
                            depAirport=DepartureAirport,  # 出发机场
                            arrAirport=ArrivalAirport,  # 到达机场
                            currency=Abbreviation,  # 货币种类
                            adultPrice=DiscountFareTotal + Total, # 成人票价
                            adultTax=DiscountFareTaxes + Total,  # 税价
                            netFare=DiscountFare,  # 净票价
                            maxSeats=SeatsAvailable,  # 可预定座位数
                            cabin=FareCategory,  # 舱位
                            carrier=flightNumber[:2],  # 航空公司
                            isChange=1,  # 是否为中转 1.直达2.中转
                            segments="[]",  # 中转时的各个航班信息
                            getTime=time.mktime(datetime.now().timetuple()).__int__(),
                            ))
                        if not item_cache or item['adultPrice'] < item_cache['adultPrice']:
                            item_cache = item.copy()

                    if item_cache['cabin'] != 'SkyBoss':
                        yield  item_cache
                    else:
                        yield None
        except:
            self.is_ok = False
            logging.error(response.body)
            logging.error('error ddddd', traceback.format_exc())
            pass

    @staticmethod
    def _get_dates(_day, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_day, '%Y-%m-%d') + timedelta(day)).strftime('%Y-%m-%d'))
        return dates
