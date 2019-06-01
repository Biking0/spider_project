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
from lamudatech_dev.pipelines import LamudatechDevPipeline

from utils.process_airport_city.get_airport_city import get_airport_city

# from utils.airports_rd import get_airports
from utils.push_date import push_date


class UoSpider(scrapy.Spider):
    name = 'uo'
    spider_name = 'uo'
    start_urls = 'https://booking.hkexpress.com/en-US'
    version = 1.0
    tax_cache = {}
    seat = 3

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection': "keep-alive",
            'Content-Type': "application/json",
            'Host': "booking.hkexpress.com",
            'Origin': "https://booking.hkexpress.com",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'X-Requested-With': "XMLHttpRequest",
            'Cache-Control': "no-cache"
        },

        DOWNLOADER_MIDDLEWARES={
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.UoProcessCookies': 500,
        },
        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        # DEPTH_PRIORITY=1,
        # DOWNLOAD_DELAY = 3,
        # DOWNLOAD_TIMEOUT = 6,
        # COOKIES_ENABLED=False,
        # HTTPERROR_ALLOWED_CODES=[500],
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

            print(result)
            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')

            # _from, _to = 'NGB', 'HKG'
            # _from, _to = 'HKG', 'NRT'
            _date = "{:%d/%m/%Y}".format(datetime.strptime(_date, "%Y%m%d") + timedelta(3))

            data = {
                'SearchType': 'Oneway',
                'OriginStation': _from,
                'DestinationStation': _to,
                'MultiOriginStation1': _from,
                'MultiDestinationStation2': _from,
                'DepartureDate': _date,
                'Adults': self.seat,
                'Children': '0',
                'Infants': '0',
                'PromotionCode': '',
                'LowFareFinderSelected': 'false'
            }

            yield scrapy.Request(self.start_urls, method='POST',
                                    body=json.dumps(data),
                                    meta={
                                        'origin': 1,
                                        '_from': _from, '_to': _to,
                                    },
                                    dont_filter=True
                                    )

            # 暂停引擎
            self.crawler.engine.pause()

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        token = meta.get('token')
        _next_date = meta.get('_next_date')

        # ajax请求
        select_departure = response.xpath('//*[@id="select_departure"]/table/tbody//input[@data-lowest="True"]/@value').extract_first()

        # 请求下一天数据时用到
        btn_next = response.xpath('//*[@id="select_departure"]/a[@class="btn_next"]')
        DepartureDate = btn_next.xpath('@data-date').extract_first()
        JourneyIndex = btn_next.xpath('@data-index').extract_first()
        Incrementer = btn_next.xpath('@data-incrementer').extract_first()
        next_headers = {
            'Accept': "application/json, text/javascript, */*; q=0.01",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection': "keep-alive",
            'Content-Type': "application/x-www-form-urlencoded",
            'Host': "booking.hkexpress.com",
            'Origin': "https://booking.hkexpress.com",
            'Referer': response.request.headers['Referer'],
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'X-Requested-With': "XMLHttpRequest",
            'Cache-Control': "no-cache"
        }

        # 解析初始页面，第一周请求入队
        if 'origin' in response.meta and response.meta['origin'] == 1:
            origin_token = response.xpath('//*[@name="__RequestVerificationToken"]/@value').extract_first()
            li_list = response.xpath('//*[@id="select_departure"]/div[@class="selectdate"]/ul/li[@class!="disabled" and @class!="current"]')
            for li in li_list:
                data_date = li.xpath('@data-date').extract_first()
                data = {"DatesSelected": [data_date],
                        "SelectedFares": [select_departure],
                        "aftoken": origin_token}
                DateTabSelect_url = self.start_urls + '/Search/DateTabSelect'
                if li == li_list[-1]:
                    yield scrapy.Request(DateTabSelect_url, method='POST',
                                         cookies=response.request.cookies,
                                         headers=response.request.headers,
                                         body=json.dumps(data),
                                         meta={'origin': 2, '_next_date': DepartureDate, 'token': origin_token,
                                               '_from': _from, '_to': _to,
                                               },
                                         priority=1,
                                         dont_filter=True)
                else:
                    yield scrapy.Request(DateTabSelect_url, method='POST',
                                         headers=response.request.headers,
                                         cookies=response.request.cookies,
                                         body=json.dumps(data),
                                         meta={'token': origin_token,
                                               '_from': _from, '_to': _to,
                                               },
                                         priority=1,
                                         dont_filter=True)
            else:
                # 更新session
                next_data = {
                    'DepartureDate': DepartureDate,
                    'JourneyIndex': JourneyIndex,
                    'Incrementer': Incrementer,
                    'aftoken': origin_token
                }
                next_date_url = self.start_urls + '/Search/NextDate'
                yield scrapy.Request(next_date_url, method='POST',
                                     headers=next_headers,
                                     cookies=response.request.cookies,
                                     body=parse.urlencode(next_data),
                                     dont_filter=True,
                                     priority=1,
                                     callback=self.parse_next
                                     )

        # 解析通用页面，价格不含税
        tr_list = response.xpath('//*[@id="select_departure"]/table/tbody/tr')
        items = []
        time_array = None
        for tr in tr_list:
            # 出发时间
            Departure = tr.xpath('td[@data-title="Departure"]')
            dep_date = Departure.xpath('span[@class="sr-only"]/text()').extract_first()
            time_array = dep_date
            dep_time = Departure.xpath('strong[@class="depart-time"]/text()').extract_first()
            data_std = dep_date+dep_time
            # 出发机场
            dep_text = Departure.xpath('text()').extract().pop()
            dep_airport = re.search(r'\w+', dep_text).group()
            # 到达时间
            Arrival = tr.xpath('td[@data-title="Arrival"]')
            arr_date = Arrival.xpath('span[@class="sr-only"]/text()').extract_first()
            arr_time = Arrival.xpath('strong[@class="arrive-time"]/text()').extract_first().split()
            data_sta = arr_date+arr_time[0]
            # 到达机场
            arr_text = Arrival.xpath('text()').extract().pop()
            arr_airport = re.search(r'\w+', arr_text).group()
            # 航班号
            Flight = tr.xpath('td[@data-title="Flight"]')
            flight_text = Flight.xpath('strong/text()').extract_first().split()
            carrier, flight_number = flight_text[-2:]

            flight_change = Flight.xpath('text()').extract().pop().strip()
            if flight_change == u"Direct Flight":
                # 价格
                Fun = tr.xpath('td[@data-title="Fun"]')
                _input = Fun.xpath('label/input')
                if _input:
                    # value = _input.xpath('@value').extract_first()
                    fun_currency, fun_price = Fun.xpath('label/span[@class="table_price"]/text()').extract_first().split()
                    fun_price = float(re.sub(r',', '', fun_price))
                    seat = self.seat
                else:
                    fun_currency, fun_price, seat = '', 0.00, 0
                # Fun_plus = tr.xpath('td[@data-title="Fun+"]')
                # UBiz = tr.xpath('td[@data-title="UBiz"]')

                fromCity = self.city_airport.get(dep_airport, dep_airport)
                toCity = self.city_airport.get(arr_airport, arr_airport)

                item = FlightsItem()
                item.update(dict(
                    flightNumber=carrier+flight_number,  # 航班号
                    depTime=int(time.mktime(time.strptime(data_std, "%Y-%m-%d%H:%M"))),  # 出发时间
                    arrTime=int(time.mktime(time.strptime(data_sta, "%Y-%m-%d%H:%M"))),  # 达到时间
                    fromCity=fromCity,  # 出发城市
                    toCity=toCity,  # 到达城市
                    depAirport=dep_airport,  # 出发机场
                    arrAirport=arr_airport,  # 到达机场
                    currency=fun_currency,  # 货币种类
                    adultPrice=fun_price,  # 成人票价
                    adultTax=0,  # 税价
                    netFare=fun_price,  # 净票价
                    maxSeats=seat,  # 可预定座位数
                    cabin='ECO',  # 舱位
                    carrier=carrier,  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="NULL",  # 中转时的各个航班信息
                    getTime=int(time.time()),
                ))

                if item['netFare'] == 0:
                    yield item
                else:
                    items.append(item)

        # 请求税
        if select_departure:
            # 先查询缓存有没有税价
            tax_cache = self.tax_cache.get("%s%s" % (_from, _to))
            if tax_cache:
                for item in items:
                    item.update(dict(
                        adultPrice=tax_cache + item['netFare'],  # 成人票价
                        adultTax=tax_cache,  # 税价
                    ))
                    yield item
            else:
                tax_url = self.start_urls + '/Search/FareSelect'
                tax_data = {
                    'JourneyFareSellKeys': [select_departure],
                    'aftoken': token
                }
                yield scrapy.Request(tax_url, method='POST',
                                     cookies=response.request.cookies,
                                     meta={'items': items,
                                           '_from': _from, '_to': _to,
                                           },
                                     body=json.dumps(tax_data),
                                     callback=self.parse_tax,
                                     dont_filter=True,
                                     priority=1)
        elif items:
            # 设置失效
            data = {'fromCity': _from, 'toCity': _to,
                    'date': '{:%Y%m%d}'.format(datetime.strptime(time_array, '%Y-%m-%d'))}
            push_date(settings.PUSH_DATA_URL,
                      params={'carrier': self.spider_name},
                      action='invalid', data_array=[data])
            # for item in items: yield item

        # 请求下一天数据
        if 'origin' in response.meta and response.meta['origin'] == 2 and \
                datetime.strptime(_next_date, '%Y-%m-%d') < (datetime.now() + timedelta(30)):
            data = {"DatesSelected": [_next_date],
                    "SelectedFares": [select_departure],
                    "aftoken": token}
            DateTabSelect_url = self.start_urls + '/Search/DateTabSelect'
            yield scrapy.Request(DateTabSelect_url, method='POST',
                                 cookies=response.request.cookies,
                                 body=json.dumps(data),
                                 meta={'origin': 2, '_next_date': DepartureDate, 'token': token,
                                       '_from': _from, '_to': _to,
                                       },
                                 dont_filter=True,
                                 priority=1)

            # 更新session
            next_data = {
                'DepartureDate': DepartureDate,
                'JourneyIndex': JourneyIndex,
                'Incrementer': Incrementer,
                'aftoken': token
            }
            next_date_url = self.start_urls + '/Search/NextDate'
            yield scrapy.Request(next_date_url, method='POST',
                                 headers=next_headers,
                                 cookies=response.request.cookies,
                                 body=parse.urlencode(next_data),
                                 dont_filter=True,
                                 priority=1,
                                 callback=self.parse_next
                                 )

        # 恢复引擎
        self.crawler.engine.unpause()

    def parse_tax(self, response):
        items = response.meta['items']
        _from = response.meta.get('_from')
        _to = response.meta.get('_to')

        totalPackage = response.xpath('//*[@id="sidebar_container"]//td[@data-feename]/@data-feemsg').extract()
        tax = sum([float(re.sub(r',','', p.split()[1])) for p in totalPackage])
        # 缓存税价
        self.tax_cache.update({"%s%s"%(_from, _to): tax})
        for item in items:
            item.update(dict(
                adultPrice=tax+item['netFare'],  # 成人票价
                adultTax=tax,  # 税价
            ))
            yield item

    def parse_next(self, response):
        print(response.body)
