# -*- coding: utf-8 -*-
import scrapy, logging, time, json, traceback
from utils import pubUtil, dataUtil
from utils.spe_util import ddUtil
from lmd_spiders import settings
from jsonpath import jsonpath
from lmd_spiders.items import LmdSpidersItem

class DdSpider(scrapy.Spider):
    name = 'dd'
    allowed_domains = ['api.nokair.com']
    start_urls = 'https://api.nokair.com/services/services.svc/REST/GetAvailability'
    isOK = True
    task = []
    version = 1.0

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS = {
            'Host': 'api.nokair.com',
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'NokAir/10 CFNetwork/811.5.4 Darwin/16.7.0',
            'Accept-Language': 'en-us',
            'Accept': '*/*',
        },

        DOWNLOADER_MIDDLEWARES = {
            'lmd_spiders.middlewares.StatisticsItem': 200,
            'lmd_spiders.middlewares.ProxyMiddleware': 300,
        },

        # CONCURRENT_REQUESTS=8,
        DOWNLOAD_TIMEOUT=30,

        DEFAULT_DATA = {
            "ClientVersion": "6.0.2",
            "UserName": "NOKIPHOAPP",
            "Password": "n03@!hOH3zOieAPq1",
            # "GetAvailabilityDetail": { # 测试某条航线可取消并修改注释
            #     "Infant": 0,
            #     "DepartureAirport": "DMK",
            #     "ArrivalAirport": "CNX",
            #     "Child": 0,
            #     "Currency": "THB",
            #     "RoundTripFlag": "0",
            #     "Adult": 1,
            #     "AgencyCode": "",
            #     "ReturnDate": "",
            #     "BoardDate": "05/05/2018",
            #     "PromotionCode": ""
            # },
            "SessionID": "B157CA09A460459C95605B94C3925E80:020518173906"
        },

        # ITEM_PIPELINES={ # 数据插入测试库
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        super(DdSpider, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl(self.name, 1)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to, days) = ddUtil.analysisData(data)  # 把获取到的data格式化
            #     (dt_st, dep, to, days) = '20180510', 'DMK', 'AM1', 20
                # self.task.append({'date':dt.replace('-', ''),
                #              'depAirport': dep,
                #              'arrAirport': to,
                #              'mins': settings.INVALID_TIME
                #             })
                data_dict={
                    'GetAvailabilityDetail': {
                        "Infant": 0,
                        "DepartureAirport": dep,
                        "ArrivalAirport": to,
                        "Child": 0,
                        "Currency": 'THB',
                        "RoundTripFlag": "0",
                        "Adult": 3,
                        "AgencyCode": "",
                        "ReturnDate": "",
                        "BoardDate": dt,
                        "PromotionCode": ""
                    }
                }
                data_dict.update(self.custom_settings.get('DEFAULT_DATA'))
                yield scrapy.Request(method='POST',
                                     url=self.start_urls,
                                     body = json.dumps(data_dict),
                                     meta = {'data_dict': data_dict},
                                     callback = self.parse,
                                     dont_filter=True,
                                     errback = lambda x: self.download_errback(x, data_dict))

    def download_errback(self, x, data):
        logging.info('error download:' + 'pls change ip')
        self.isOK = False
        yield scrapy.Request(method='POST',
                             url=self.start_urls,
                             body=json.dumps(data),
                             callback=self.parse,
                             meta={'data_dict': data},
                             dont_filter=True,
                             errback=lambda x: self.download_errback(x, data))

    def parse(self, response):
        try:
            response_dict = json.loads(response.body)
            journeys = jsonpath(response_dict, '$..Journeys')
            code = response_dict.get('Code')
            if not journeys or not len(journeys):
                if not int(code):
                    return
                logging.info('not journeys... ')
                print(response.body)
                data_dict = response.meta.get('data_dict')
                yield scrapy.Request(method='POST',
                                     url=self.start_urls,
                                     body=json.dumps(data_dict),
                                     meta={'data_dict': data_dict},
                                     dont_filter=True,
                                     callback = self.parse,
                                     errback=lambda x: self.download_errback(x, data_dict))
                return
            currency = jsonpath(response.meta, '$..Currency')[0]
            journeys = journeys[0]
            for journey in journeys:
                infos = journey.get('TravelInfos')
                if len(infos) > 1:
                    continue
                info = infos[0]
                dep = info.get('DepartureAirportCode')
                arr = info.get('ArrivalAirportCode')
                try:
                    depTime = ddUtil.str_to_stamp(info.get('DepartureDate'))
                    arrTime = ddUtil.str_to_stamp(info.get('ArrivalDate'))
                except:
                    logging.info('the format of date is error!')
                    self.isOK = False
                    data_dict = response.meta.get('data_dict')
                    data_info = data_dict.get('GetAvailabilityDetail')
                    print(data_info.get('DepartureAirport'), data_info.get('ArrivalAirport'), data_info.get('BoardDate'))
                    yield scrapy.Request(method='POST',
                                         url=self.start_urls,
                                         body=json.dumps(data_dict),
                                         meta={'data_dict': data_dict},
                                         dont_filter=True,
                                         callback = self.parse,
                                         errback=lambda x: self.download_errback(x, data_dict))
                    break
                flightNumber = info.get('FlightNumber')
                aircraft = info.get('EquipmentType')
                cabin = info.get('ClassCode')
                duration = ddUtil.format_duration(info.get('TravelDuration'))
                carrier = info.get('CarrierCode')
                fare = journey.get('FlyFare')
                bagfare = journey.get('FlyBagFare')
                bageatfare = journey.get('FlyBagEatFare')
                lowfare = fare
                if not lowfare:
                    seats, price, tax = 0, 0, 0
                else:
                    if bagfare and lowfare.get('FareAmount') > bagfare.get('FareAmount', 999999):
                        lowfare = bagfare
                    if bageatfare and lowfare.get('FareAmount') > bageatfare.get('FareAmount', 99999):
                        lowfare = bageatfare
                    seats = lowfare.get('AvailableCount')
                    price = lowfare.get('FareAmount')
                    tax = jsonpath(lowfare, '$..Amount')[0]
                    if price == tax:
                        logging.info('price == tax')
                        self.isOK = False
                        data_dict = response.meta.get('data_dict')
                        yield scrapy.Request(method='POST',
                                             url=self.start_urls,
                                             body=json.dumps(data_dict),
                                             meta={'data_dict': data_dict},
                                             dont_filter=True,
                                             callback = self.parse,
                                             errback=lambda x: self.download_errback(x, data_dict))
                        break
                self.isOK = True
                segment = dict(
                    flightNumber = flightNumber,
                    aircraftType = aircraft,
                    number = 1,
                    airline = carrier,
                    dep = dep,
                    dest = arr,
                    duration = duration,
                    departureTime = dataUtil.format_seg_time(depTime),
                    destinationTime = dataUtil.format_seg_time(arrTime),
                    depTerminal = '',
                    seats = seats
                )

                item = LmdSpidersItem()
                item.update(dict(
                    carrier = carrier,
                    maxSeats = seats,
                    flightNumber = flightNumber,
                    depTime = depTime,
                    arrTime = arrTime,
                    depAirport = dep,
                    arrAirport = arr,
                    cabin = cabin,
                    currency = currency,
                    isChange = 1,
                    getTime = time.time(),
                    adultPrice = price,
                    adultTax = tax,
                    netFare = price - tax,
                    fromCity = self.portCitys.get(dep, dep),
                    toCity = self.portCitys.get(arr, arr),
                    segments = json.dumps([segment]),
                ))

                yield item
        except:
            traceback.print_exc()
            print(response.body)