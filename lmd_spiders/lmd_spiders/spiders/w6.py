# -*- coding: utf-8 -*-
import scrapy, time, logging, json, random
from lmd_spiders.items import LmdSpidersItem
from utils import dataUtil, pubUtil
from utils.spe_util import vyUtil
from datetime import datetime, timedelta
from jsonpath import jsonpath


class W6Spider(scrapy.Spider):
    name = 'w6'
    allowed_domains = ['mobilelivea2.mobile.wizzair.com']
    start_urls = [
        'https://mobilelivea2.mobile.wizzair.com/V8_1/OperationService/GetShortenTimeTable',
        'https://mobilelivea2.mobile.wizzair.com/V8_1/SearchFlightService/SearchFlight',
    ]
    carrier = 'W6'
    task = []
    version = 1.9
    isOK = True

    custom_settings = dict(

        HEADERS_LIST = [
            {'Accept-Encoding': 'gzip'},
            {'X-NewRelic-ID': 'Uw8GWF9VGwAHUFFVAQQF'},
            {'User-Agent': 'wizz-air/5.8.1 (com.wizzair.WizzAirApp; build:580; iOS 10.3.3) Alamofire/4.7.2'},
            {'Host': 'mobilelivea2.mobile.wizzair.com'},
            # {'Accept-Language': 'zh-Hans-CN;q=1.0, en-CN;q=0.9, en-US;q=0.8'},
            {'Content-Type': 'application/json'},
            {'Accept-Language': 'zh-Hans-CN;q=1.0, en-CN;q=0.9, en-US;q=0.8'},
            {'Connection': 'keep-aive'},
            {'Accept': 'application/json'},
            {'Are-You-Human': 'please anwser'},
        ],

        DEFAULT_REQUEST_HEADERS={
            'Accept-Encoding': 'gzip',
            'X-NewRelic-ID': 'Uw8GWF9VGwAHUFFVAQQF',
            'User-Agent': 'wizz-air/5.7.1 (com.wizzair.WizzAirApp; build:580; iOS 10.3.3) Alamofire/4.7.2',
            # 'Accept-Language': 'zh-Hans-CN;q=1.0, en-CN;q=0.9, en-US;q=0.8',
            'Host': 'mobilelivea2.mobile.wizzair.com',
            'Content-Type': 'application/json',
            # 'Accept-Encoding': 'gzip',
            'Connection': 'keep-aive',
            'Accept': 'application/json',
        },

        CONCURRENT_REQUESTS=1,
        # DOWNLOAD_DELAY=0.1,

        # LOG_LEVEL='DEBUG',

        GET_SESSION_URL = 'https://mobilelivea2.mobile.wizzair.com/V8_1/SessionService/GetSession',

        BASE_DATA = {
            "Process": {
                "ClientId": "WizzAir-iPhone-v5.8.1",
                # "ClientInstanceId": "660ADADA-E337-42BA-8E70-572E0DC56012",
                "ClientInstanceId": "9364A5FD-A7F1-4330-9C4D-CA509D2FEB20",
                "Environment": "PROD"
            },
            "Device": {
                "RegionFormat": "zh_CN",
                "TimeZone": "GMT+8",
                "Calendar": "gregorian",
                "Type": "iPhone 6",
                "Localization": "zh-CN",
                "Version": "10.3.3"
            },
        },

        GET_SESSION_DATA = {  # 获取sessionid和cookie所需的data
            "UserName": "_srv_xyz_api",
            "Token": "SkCDOHwanB6mTXD3HhpZ"
        },

        GET_DATE_DATA={  # 获取时间表所需要的data
            # "DepartureDate": "2018-06-04",
            # "DepartureStation": "TIA",
            # "ArrivalStation": "LTN"
        },


        DEFAULT_DATA={  # 获取航班数据所需的data
            # "DepartureStation": "ATH",
            # "DepartureDate": "2018-06-09",
            # "ArrivalStation": "LTN",
            "AdultNum": 3,
            "JourneyType": ""
        },

        DOWNLOAD_TIMEOUT=20,

        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        COOKIES_ENABLED=True,
        DOWNLOADER_MIDDLEWARES={
            'lmd_spiders.middlewares.StatisticsItem': 200,
            'lmd_spiders.middlewares.W6CookieMiddleware': 300,
        },

        # ITEM_PIPELINES={ # 往测试库添加数据
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        super(W6Spider, self).__init__(*args, **kwargs)
        self.custom_settings['GET_SESSION_DATA'].update(self.custom_settings.get('BASE_DATA'))
        self.custom_settings['GET_DATE_DATA'].update(self.custom_settings.get('BASE_DATA'))
        self.custom_settings['DEFAULT_DATA'].update(self.custom_settings.get('BASE_DATA'))
        self.custom_settings['DEFAULT_REQUEST_HEADERS'] = self.get_headers()
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        self.get_headers()
        while True:
            result = pubUtil.getUrl(self.name, 1)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to, days) = vyUtil.analysisData(data)  # 把获取到的data格式化
                # (dt, dep, to, days) = ('20181026', 'LTN', 'IAS', 30)
                dt_datetime = datetime.strptime(dt, '%Y%m%d')
                end_date = dt_datetime + timedelta(days=int(days))
                dt = dt_datetime.strftime('%Y-%m-%d')
                data_post = dict(
                    DepartureDate=dt,
                    DepartureStation=dep,
                    ArrivalStation=to,
                )
                data_post.update(self.custom_settings.get('GET_DATE_DATA'))
                yield scrapy.Request(method='POST',
                                     url=self.start_urls[0],
                                    #  formdata=data_post,
                                     body=json.dumps(data_post), 
                                     headers=self.custom_settings.get('DEFAULT_REQUEST_HEADERS'),
                                     meta={'end_date': end_date},
                                     dont_filter=True,
                                     callback=self.date_parse,
                                     errback=lambda x: self.download_errback(x, data_post, end_date),
                                     )

    def download_errback(self, x, data_post, end_date):
        self.isOK = False
        logging.info('error downloading ....')
        yield scrapy.Request(method='POST',
                             url=self.start_urls[0],
                             body=json.dumps(data_post),
                             headers=self.custom_settings.get('DEFAULT_REQUEST_HEADERS'),
                             meta={'end_date': end_date, 'data_post': data_post},
                             dont_filter=True,
                             callback=self.date_parse,
                             errback=lambda x: self.download_errback(x, data_post, end_date),
                             )

    def date_parse(self, response):
        # print(response.text)
        # print(type(response.body))
        null = ''
        true = 'true'
        false = 'false'
        try:
            data_dict = eval(response.text)
        except:
            logging.info('pls update headers')
            end_date = response.meta.get('end_date')
            data_post = response.meta.get('data_post')
            self.get_headers()
            yield scrapy.Request(method='POST',
                                 url=self.start_urls[0],
                                 body=json.dumps(data_post),
                                 meta={'end_date': end_date, 'data_post': data_post},
                                 dont_filter=True,
                                 headers=self.custom_settings.get('DEFAULT_REQUEST_HEADERS'),
                                 callback=self.date_parse,
                                 errback=lambda x: self.download_errback(x, data_post, end_date),
                                 )
            return
        # data_dict = json.loads(response.text)
        flights = data_dict.get('FlightDates')
        end_date = response.meta.get('end_date')
        self.isOK = True
        if not flights:
            return
        for flight in flights:
            dep = flight.get('DepartureStation')
            arr = flight.get('ArrivalStation')
            dates = flight.get('Dates')
            for date in dates:
                dt_datetime = datetime.strptime(date, '%Y-%m-%d')
                if dt_datetime > end_date:
                    break
                data_post = dict(
                    DepartureDate=date,
                    DepartureStation=dep,
                    ArrivalStation=arr,
                )
                data_post.update(self.custom_settings.get('DEFAULT_DATA'))
                self.get_headers()
                yield scrapy.Request(method='POST',
                                     url=self.start_urls[1],
                                     body=json.dumps(data_post),
                                     headers=self.custom_settings.get('DEFAULT_REQUEST_HEADERS'),
                                     meta={'data_post': data_post},
                                     dont_filter=True,
                                     callback=self.parse)

    def parse(self, response):
        # print(response.body)
        null = ''
        true = 'true'
        false = 'false'
        try:
            data_dict = eval(response.text)
        except:
            logging.info('pls update headers')
            data_post = response.meta.get('data_post')
            self.get_headers()
            yield scrapy.Request(method='POST',
                                 url=self.start_urls[1],
                                 headers=self.custom_settings.get('DEFAULT_REQUEST_HEADERS'),
                                 body=json.dumps(data_post),
                                 meta={'data_post': data_post},
                                 dont_filter=True,
                                 callback=self.parse)
            return
        # data_dict = json.loads(response.body)
        journeys = data_dict.get('Journeys')
        currency = data_dict.get('CurrencyCode')
        for journey in journeys:
            depAirport = journey.get('DepartureStation')
            arrAirport = journey.get('ArrivalStation')
            carrier = journey.get('CarrierCode')
            flightNumber = carrier + journey.get('FlightNumber')
            depTime = time.mktime(time.strptime(journey.get('STD'), '%Y-%m-%dT%H:%M:%S'))
            arrTime = time.mktime(time.strptime(journey.get('STA'), '%Y-%m-%dT%H:%M:%S'))
            fares = jsonpath(journey, '$..Fares')[0]
            lowFare = dict(
                adultPrice=0,
                netFare=0,
                maxSeats=0,
                adultTax=0,
                cabin='',
            )
            # 增加套餐价格,先定义价格表
            price_dict = {
                'Basic': 0,
                'Middle': 0,
                'Plus': 0,
                'SUPER_ECO': 0
            }
            lowest = None
            for fare in fares:
                if fare.get('ProductClass') == 'WC': # 排除掉wizz club的价格，注释掉即是会员折扣价
                    continue

                paxFareTypes = fare.get('PaxFares')[0].get('PaxFareTypes')
                for paxfare in paxFareTypes:
                    package_name = paxfare.get('PaxFareClass')
                    package_price = max(jsonpath(paxfare, '$..Amount'))
                    price_dict[package_name] = package_price

                paxfare = paxFareTypes[0]
                price = max(jsonpath(paxfare, '$..Amount'))
                netfare = paxfare.get('PureFarePriceAmount')
                lowFare['adultPrice'] = price
                lowFare['netFare'] = netfare
                lowFare['maxSeats'] = fare.get('AvailableCount')
                lowFare['cabin'] = fare.get('ProductClass')
                lowFare['adultTax'] = price - netfare
                break


            # segments = '%s:%s' % (price_dict.get('Middle'), price_dict.get('Plus'))
            segments = [[price_dict.get('Middle'), lowFare.get('maxSeats')],
                        [price_dict.get('Plus'), lowFare.get('maxSeats')]]

            item = LmdSpidersItem()
            item.update(dict(
                flightNumber=flightNumber,
                depAirport=depAirport,
                arrAirport=arrAirport,
                carrier=carrier,
                depTime=depTime,
                arrTime=arrTime,
                currency=currency,
                segments=json.dumps(segments),
                isChange=1,
                getTime=time.time(),
                fromCity=self.portCitys.get(depAirport, depAirport),
                toCity=self.portCitys.get(arrAirport, arrAirport),
            ))
            item.update(lowFare)
            yield item

    def get_headers(self):
        lis = self.custom_settings.get('HEADERS_LIST')
        random.shuffle(lis)
        headers = {}
        for li in lis:
            headers = dict(headers, **li)
        self.custom_settings['DEFAULT_REQUEST_HEADERS'] = headers


