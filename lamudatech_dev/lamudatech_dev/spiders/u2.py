# -*- coding: utf-8 -*-
import re
import sys
import json
import time
import scrapy
import requests
import jsonpath
import traceback
from datetime import datetime, timedelta

# 兼容Python3
try:
    from urllib import parse
except:
    import urllib as parse

from lamudatech_dev.pipelines import LamudatechDevPipeline
from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings
from utils.process_airport_city.get_airport_city import get_airport_city
# from utils.u2.airports_rd import get_airports
from utils.push_date import push_date
from utils import pubUtil


class EjSpiderSpider(scrapy.Spider):
    name = 'u2'
    spider_name = 'u2'
    version = 3.0 

    start_urls = 'https://www.easyjet.com/ejavailability/api/v25/availability/query?'
    is_ok = True
    proxy = None
    search_seats = 3
    currency_cache = {
        'CSK': 'CZK'
    }

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'ADRUM': "isAjax:true",
            'Connection': "keep-alive",
            'Host': "www.easyjet.com",
            'Referer': "https://www.easyjet.com/en/buy/flights?isOneWay=on&pid=www.easyjet.com",
            'User-Agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Mobile Safari/537.36",
            'X-Requested-With': "XMLHttpRequest",
            'Cache-Control': "no-cache",
        },

        DOWNLOADER_MIDDLEWARES={
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.U2ProcessCookies': 500,
        },

        CITY_FULL=dict(
            LTN='#LONDON',
            LCY='#LONDON',
            LGW='#LONDON',
            LHR='#LONDON',
            SEN='#LONDON',
            STN='#LONDON',
            LON='#LONDON',

            BER='#BERLIN',
            SXF='#BERLIN',
            TXL='#BERLIN',

            PAR='#PARIS',
            BVA='#PARIS',
            XCR='#PARIS',
            CDG='#PARIS',
            ORY='#PARIS',

            BGY="#MILAN",
            PMF="#MILAN",
            MXP="#MILAN",

            TFS='#CANARY ISLANDS',
            TFN='#CANARY ISLANDS',

            AJA='#CORSICA',
            BIA='#CORSICA',
            FSC='#CORSICA',

            HER='#CRETE',
            CTA='#SICILY',
            OLB='#SARDINIA',
            EDI='#CENTRAL SCOTLAND',

        ),

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        HTTPERROR_ALLOWED_CODES=[403],

        # DOWNLOAD_DELAY = 3,
        DOWNLOAD_TIMEOUT=30,
        # COOKIES_ENABLED=False,
        # LOG_FILE = 'log/%s-spider.log' % spider_name,
        # LOG_LEVEL='DEBUG',

        # 仅供测试用
        # ITEM_PIPELINES = {
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        permins = 0
        self.proxy = True
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pubUtil.get_task(self.name, step=7)
                result = next(result_iter)
            else:
                try:
                    data_api = settings.GET_TASK_URL + 'carrier=U2'
                    result = json.loads(requests.get(data_api, timeout=180).text).get('data')
                except Exception as e:
                    self.log(e)
                    result = None

            if not result:
                self.log('Date is None!', level=20)
                self.log('Waiting...', level=20)
                time.sleep(16)
                continue

            airports, _day, _num = result[0].split(':')
            FROM, TO = airports.split('-')
            # FROM, TO = 'TXL', 'ARN'

            lowfares_url = 'https://www.easyjet.com/ejcms/cache15m/api/routedates/get/?'
            lowfares_total_url = lowfares_url + parse.urlencode({'originIata': FROM, 'destinationIata': TO})

            yield scrapy.Request(lowfares_total_url,
                                 meta={'FROM': FROM, 'TO': TO},
                                 callback=self.date_parse,
                                 errback=self.errback,
                                 dont_filter=True)

    def errback(self, failure):
        self.log(failure.value, 40)
        self.is_ok = False
        return failure.request

    def date_parse(self, response):
        meta = response.meta
        city_full = self.custom_settings.get('CITY_FULL')
        FROM = city_full.get(meta.get('FROM'), meta.get('FROM'))
        TO = city_full.get(meta.get('TO'), meta.get('TO'))

        Months = jsonpath.jsonpath(json.loads(response.text), '$..Months.*')
        flag = datetime.now() + timedelta(45)
        for i, rec in enumerate(Months):
            YearNumber = rec.get('YearNumber')
            MonthNumber = rec.get('MonthNumber')
            FlightDates = rec.get('FlightDates')
            for date in self.compress_list(FlightDates):
                min_day, mid_day, max_day = date
                min_date = '%s-%s-%s' % (YearNumber, MonthNumber, min_day)
                mid_date = '%s-%s-%s' % (YearNumber, MonthNumber, mid_day)
                max_date = '%s-%s-%s' % (YearNumber, MonthNumber, max_day)
                # min_date, max_date = '2018-12-04', '2018-12-06'
                # 过滤掉45天后的日期
                if flag > datetime.strptime(min_date, "%Y-%m-%d"):
                    params = parse.urlencode(dict(
                        AdditionalSeats=0,
                        AdultSeats=self.search_seats,  # U2后台有税价的搜索一个人比搜索三个人的价格要高. 但是本爬虫也已经把税转换成单人的总税
                        ChildSeats=0,
                        DepartureIata=FROM,
                        ArrivalIata=TO,
                        IncludeAdminFees='true',
                        IncludeFlexiFares='true',
                        IncludeLowestFareSeats='true',
                        IncludePrices='true',
                        Infants=0,
                        IsTransfer='false',
                        LanguageCode='EN',
                        MaxDepartureDate=max_date,
                        MinDepartureDate=min_date,
                    ))
                    total_url = self.start_urls + params

                    yield scrapy.Request(total_url,
                                         callback=self.parse,
                                         meta={'FROM': meta.get('FROM'), 'TO': meta.get('TO'), '_day': (min_date, mid_date, max_date)},
                                         dont_filter=True
                                         )
                else:
                    return

    def parse(self, response):
        # 给设置无效用的。。。。
        from_port = response.meta.get('FROM')
        to_port = response.meta.get('TO')
        FROM = self.city_airport.get(from_port, from_port)
        TO = self.city_airport.get(to_port, to_port)
        list_day = response.meta.get('_day')

        # 创建items实例
        item = FlightsItem()
        response_dict = json.loads(response.body)
        try:
            # 使用jsonpath获取元素
            AvailableFlights = response_dict.get('AvailableFlights')
            DisplayCurrencyCode = response_dict.get('DisplayCurrencyCode')

            for i in AvailableFlights:
                price_pack = [[0, 0]]
                adult_price = sys.maxint
                seats = 0
                for price_item in i.get('FlightFares'):
                    i_Price = jsonpath.jsonpath(price_item, '$..Price')
                    if not i_Price:
                        continue
                    i_Price = i_Price[0]
                    PriceWithDebitCard = jsonpath.jsonpath(price_item, '$..PriceWithDebitCard')[0]
                    i_tax = self.get_tax(i_Price, PriceWithDebitCard)
                    i_seat = price_item.get('LowestFareSeatsAvailable')

                    i_adult_price = i_Price + i_tax
                    if price_item.get('FareType') == 'Flexi':
                        price_pack[0] = [i_Price + i_tax, i_seat]
                    if i_adult_price < adult_price and i_adult_price != 0:
                        adult_price, seats, Price, tax = i_adult_price, i_seat, i_Price, i_tax
                if adult_price == sys.maxint:
                    adult_price, seats, Price, tax = [0] * 4
                depTime = i.get('LocalDepartureTime')
                arrTime = i.get('LocalArrivalTime')

                dep_port = i.get('DepartureIata')
                arr_port = i.get('ArrivalIata')

                from_city = self.city_airport.get(dep_port, dep_port)
                to_city = self.city_airport.get(arr_port, arr_port)

                item['flightNumber'] = "U2%s" % i.get('FlightNumber')  # 航班号
                item['depTime'] = time.mktime(time.strptime(depTime, "%Y-%m-%dT%H:%M:%S")).__int__()  # 出发时间
                item['arrTime'] = time.mktime(time.strptime(arrTime, "%Y-%m-%dT%H:%M:%S")).__int__()  # 达到时间
                item['fromCity'] = from_city  # 出发城市
                item['toCity'] = to_city  # 到达城市
                item['depAirport'] = dep_port  # 出发机场
                item['arrAirport'] = arr_port  # 到达机场
                item['currency'] = self.currency_cache.get(DisplayCurrencyCode, DisplayCurrencyCode)  # 货币种类
                item['adultPrice'] = adult_price  # 成人票价
                item['adultTax'] = tax  # 税价
                item['netFare'] = Price  # 净票价
                item['maxSeats'] = seats  # 可预定座位数
                item['cabin'] = "Y"  # 舱位
                item['carrier'] = "U2"  # 航空公司
                item['isChange'] = 1  # 是否为中转 1.直达2.中转
                item['segments'] = json.dumps(price_pack)  # 中转时的各个航班信息
                item['getTime'] = time.mktime(datetime.now().timetuple()).__int__()
                yield item
        except Exception as e:
            # traceback.print_exc()
            # print(response.body)
            self.log(e, level=40)

            # 设置失效
            params = {'carrier': 'U2'}

            data_array = list()
            for _day in list_day:
                data = {
                    'fromCity': FROM,
                    'toCity': TO,
                    'date': re.sub(r'(\d+)-(\d+)-(\d+)', r'\1\2\3', _day),
                }
                data_array.append(data)

            res = push_date(settings.PUSH_DATA_URL, params=params,
                      action='invalid', data_array=data_array)
            self.log('%s-%s: %s no flights'%(FROM, TO, list_day), level=20)
            pass

    def get_tax(self, base_price, tax_price):
        """
        获取该低价的单人总税
        :param base_price: 不含税低价
        :param tax_price: 搜索多人时的含税单价
        :return: 搜索一人时该低价的所对应的税
        """
        per_tax = tax_price - base_price
        tax = per_tax * self.search_seats
        return tax

    @staticmethod
    def compress_list(days):
        b_list = []
        for i in days:
            if i in b_list:
                continue
            b_list.append(i)
            if i + 1 <= days[-1]:
                b_list.append(i + 1)
            else:
                b_list.append(i)
            if i + 2 <= days[-1]:
                b_list.append(i + 2)
            else:
                b_list.append(b_list[-1])
            yield b_list[-1:-4:-1][::-1]
