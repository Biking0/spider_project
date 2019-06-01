# -*- coding: utf-8 -*-
import os
import re
import csv
import time
import json
import random
import logging
from datetime import datetime, timedelta

import scrapy
from jsonpath import jsonpath

from lmd_spiders import settings
from utils.spe_util import vyUtil
from utils import pubUtil, dataUtil
from lmd_spiders.items import LmdSpidersItem


class VySpider(scrapy.Spider):
    name = 'vy'
    allowed_domains = ['vueling.com']
    start_url = 'https://apimobile.vueling.com/Vueling.Mobile.AvailabilityService.WebAPI/api/AvailabilityController/DoAirPriceSB'
    carrier = 'VY'
    task = []
    isOK = True
    cookie = ''
    version = 2.3
    cookies = [
        'sto-id-47873-%3FFE-PRO%3Fmaqueta-waf-mobile-443=ADBEKIMALLAB; ak_bmsc=971CA00C1B3C0EE405820C1BD70EC3ABDF77F85D1E2F0000C556075B7D87485C~plp0RWi2rN+sNIkga3IY591kobvkfBH2JJPnGS12ucAudZZGhb7lneTvmBzgeizzjeyVzDvIR9aMqVYO+wzQrIQcDfLCHQ8ZDgnHRt+Gxc9kvcEYJTz6f+Cn8PP5ZTaXDO7qQA6FRPjLh76uKAOLrNgkPMQ1D1MaIa+iDwLo8jHxAAXS0U8RAWe1w3bY6X4NIoO1RlSuRFLoZqdkjc5UZiP8QapVS3SyLqAMPJeL3yB1w=',
        'sto-id-47873-%3FFE-PRO%3Fmaqueta-waf-mobile-443=ACBEKIMALLAB; ak_bmsc=D46CD922B8008E17B75EB4DFC6479A06B8325774A616000086310E5BA08FC12E~plInDegCfE0SBXDYY1yL7wkXEU6qCOtq4dxVXG9rAW+Wuk8Gmb0pejgeni0HRTOin10bIi3o7H7hXLDyq0a9IBlxy6u3afgH6r+ftXxb8G1zVUV1lVGDiN08LnpjDUW37f1hwyXlKm5k5asitnh+n2dNyU/LZOigR/q9WbDOdNBzIyTTSNOArwvagkZVIcXX+N1hU6j+lC2pOnjA4FDOAlUaTykukAxIURCH9LFyWcg+I=',
        'sto-id-47873-%3FFE-PRO%3Fmaqueta-waf-mobile-443=ACBEKIMALLAB; ak_bmsc=523E87D358BC4F53525FC0D12416D9CEB8325774A6160000B4F80D5BDA868302~plN2M/xIrHbeMymLfw2YU5nk0gkLLblR6RLUDOAK5b1hPsOxIPJ8RgGHNHLuWqvai/RcvJoO0GlVVOn2I47aAwMFPkp1uqoP6uIdO5ROcxD+LLHklcpJrsYDw7ie02ynE4k46zbniLp7Sohb+In8zpTA4pPnkCUY68e4JNV88llQsMEgvTtwIueFoEffuH7mHTuAwjlD0pVv4+LL1LTI39SaYqX80XJsk2C7H2d0QmKBA=',
        'sto-id-47873-%3FFE-PRO%3Fmaqueta-waf-mobile-443=AEBEKIMALLAB; ak_bmsc=82EFD170AD927AF4B48121500CA6B274DF77F85D287800007BAA145B8554D751~plM1H7g6D8gXG21kQ/zLBCkhxULlHG9oLJnASEUsxSBPMH4UryidFVI5crQRV2t1j2mt2yUHDFosVc3graM0X8pmI26ySgLpIBzsxB0Mp9ivVPaJLarF/0P85KIL54Iy9xizLj6MTXymkzzlVmeMJpd//H0nze/PNd12GezLvD1bQkDSXOWxkYfqrU7ZPcfjZiq0d/XP2QJ/ZXtC7DUtv7Cflsx0lXsV6oqmS6PD4pPy4=',
        'sto-id-47873-%3FFE-PRO%3Fmaqueta-waf-mobile-443=ADBEKIMALLAB; ak_bmsc=8E1FFA075B81CD3357D8F32F940C044EB832575FE12000006FAE145BADF7112D~plp7ePSyhFBSVZ6OgAf5ZpmeER/jJaPldvhkBCGeyrZhym72YrEWaEOJoPjSEa5FMqXngPxTzWc8YZgQd2pXcD2njhTzVnHl7QaAdZpbjGwNnBiBuOhub8im2Qa5BX57QeiLgFVmhRIMxjKcCAkGftIQu1PlIRF7W9Esu1oefYT5UVVpgh6t4BOJ195yPm1JSG5OBFiSXfzX8k4K4r5aUtblZkB3qvwCZAq48zEUA0Nyc=',
    ]
    InstallationID = [
        '9AC6A648-98AE-4875-8451-DA948F84D777',
        'DBB3A54A-8132-4B1B-A28A-B360335B4820',
        '3BAE1C15-5389-44C6-955C-D04B3BABEF03',
        'F99526E6-74F5-4640-B433-D4DFC2743E5B',
        '716472B4-4DE6-4559-BD89-30C560FF7803',
    ]

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Host': 'apimobile.vueling.com',
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'Accept-Language': 'en-us',
            'User-Agent': 'Vueling/881 CFNetwork/811.5.4 Darwin/16.7.0',
            #'Cookie': ''
        },
        DEFAULT_DATA={
            "DiscountType": 0,
            "IsCompletPrice": False,
            "AppVersion": "904",
            "DeviceModel": "iPhone 6P",
            "CurrencyCode": "EUR",
            "TimeZone": 8,
            "Language": "en-EN",
            "Xid": "",
            #"InstallationID": "",
            "Paxs": [{
                "Paxtype": "ADT",
                "Quantity": 3
            }, {
                "Paxtype": "CHD",
                "Quantity": 0
            }, {
                "Paxtype": "INF",
                "Quantity": 0
            }],
            # 'AirportDateTimeList': [ # 如果要单独抓取某个航线，可修改以下内容并去掉注释即可
            #     {
            #         'MarketDateDeparture': '2018-11-03T00:00:00',
            #         'DepartureStation': 'ALG',
            #         'ArrivalStation': 'BCN',
            #     }
            # ],
            "OsVersion": "10.3.3",
            "Currency": "EUR",
            "DeviceType": "IOS",
        },

        DOWNLOAD_TIMEOUT=20,

        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        COOKIES_ENABLED=True,
        DOWNLOADER_MIDDLEWARES={
             'lmd_spiders.middlewares.StatisticsItem': 200,
             'lmd_spiders.middlewares.ProxyMiddleware': 300,
         },



        CONCURRENT_REQUESTS=4,
        # LOG_LEVEL='DEBUG',

        # ITEM_PIPELINES={ # 往测试库添加数据
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        super(VySpider, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pubUtil.get_task(self.name)
                result = next(result_iter)
            else:
                result = pubUtil.getUrl(self.carrier, 1)
            if not result:
                time.sleep(6)
                continue
            hour = datetime.now().hour + 2
            self.cookie = self.cookies[hour % len(self.cookies)]
            installid = self.InstallationID[hour % len(self.InstallationID)]

            for data in result:
                (dt_st, dep, to, days) = vyUtil.analysisData(data)  # 把获取到的data格式化
                # dep, to = 'CDG', 'VIE'
                for i in range(int(days)):
                    dt = vyUtil.get_real_date(dt_st, i)
                    # dt = '2018-11-01'
                    self.task.append({
                        'date': dt.replace('-', ''),
                        'depAirport': dep,
                        'arrAirport': to,
                        'mins': settings.INVALID_TIME
                    })
                    dt = dt + 'T00:00:00'
                    data_list = {
                        'InstallationID': installid,
                        'AirportDateTimeList': [
                            {
                                'MarketDateDeparture': dt,
                                'DepartureStation': dep,
                                'ArrivalStation': to,
                            }
                        ]
                    }

                    data_list.update(self.custom_settings.get('DEFAULT_DATA'))
                    yield scrapy.Request(method='POST',
                                         url=self.start_url,
                                         headers={'Cookie': self.cookie},
                                         body=json.dumps(data_list),
                                         meta={'data_list': data_list},
                                         callback=self.parse,
                                         dont_filter=True,
                                         errback=lambda x: self.download_errback(x, data_list))

    def download_errback(self, x, data):
        logging.info('error download:' + 'pls change ip')
        self.isOK = False
        yield scrapy.Request(method='POST',
                             url=self.start_url,
                             headers = {'Cookie': self.cookie},
                             body=json.dumps(data),
                             callback=self.parse,
                             meta={'data_list': data},
                             dont_filter=True,
                             errback=lambda x: self.download_errback(x, data))

    def parse(self, response):
        try:
            response_dict = json.loads(response.body)
            journeys = jsonpath(response_dict, '$..Journeys')[0]
        except:
            if response.body.lower().find('<title>access denied</title>') != -1:
                logging.info('access denied!!!')
                self.isOK = False
            else:
                logging.info(response.body)
                return
            data_list = response.meta['data_list']
            yield scrapy.Request(method='POST',
                                 url=self.start_url,
                                 headers={'Cookie': self.cookie},
                                 body=json.dumps(data_list),
                                 meta={'data_list': data_list},
                                 callback=self.parse,
                                 dont_filter=True,
                                 errback=lambda x: self.download_errback(x, data_list))
            return
        self.isOK = True
        for journey in journeys:
            segments = journey.get('Segments')
            if len(segments) > 1:
                continue
            dep = journey.get('DepartureStation')
            arr = journey.get('ArrivalStation')
            dep_time = vyUtil.date_to_stamp(journey.get("STD"))
            arr_time = vyUtil.date_to_stamp(journey.get("STA"))

            fares = journey.get('JourneyFare')

            index_flag = -1
            seats = 1
            for i in range(len(fares)): # 找出最低价且有票的舱位
                fare = fares[i]
                if fare.get('IsFareAvailable'):
                    seats = fare.get('AvailableCount')
                    if not seats or seats >= 3:
                        index_flag = i
                        break
            if index_flag == -1:
                continue
            fare = fares[index_flag]
            seats = 9 if not seats else seats
            currency = fare.get('CurrencyCode')
            cabin = fare.get('ProductClass')
            price = fare.get('Amount')

            seg = segments[0]
            carrier = seg.get('CarrierCode')
            flightNumber = carrier + seg.get('FlightNumber')
            if not self.filter_number(flightNumber):
                continue

            flightkey = seg.get('SegmentSellKey')
            farekey = fare.get('JourneyFareKey')
            info = dict(
                flightkey=flightkey,
                farekey=farekey
            )

            # 添加segments
            price_a = [[0, 0]] * 2

            # 如果运营商不是vueling, 则座位数为0
            opt_by = journey.get('OperatedBy')
            if not opt_by in ['Vueling', 'WonderFly']:
                print(opt_by)
                seats = 0
            else:

                for i, fare in enumerate(fares[1:]):
                    flag = fare.get('Active')
                    if not flag:
                        continue
                    seat_i = fare.get('AvailableCount')
                    amt = fare.get('Amount')
                    farekey = fare.get('JourneyFareKey')
                    info_i = json.dumps(
                        dict(
                            flightkey=flightkey,
                            farekey=farekey
                        )
                    )
                    price_a[i] = [amt, 9 if not seat_i else seat_i, info_i]
            item = LmdSpidersItem()
            item['maxSeats'] = seats
            item['flightNumber'] = flightNumber
            item['depTime'] = dep_time
            item['arrTime'] = arr_time
            item['depAirport'] = dep
            item['arrAirport'] = arr
            item['currency'] = currency
            item['cabin'] = cabin
            item['carrier'] = carrier
            item['segments'] = json.dumps(price_a)
            item['isChange'] = 1
            item['getTime'] = time.time()
            item['adultPrice'] = price
            item['netFare'] = price
            item['fromCity'] = self.portCitys[dep]
            item['toCity'] = self.portCitys[arr]
            item['info'] = json.dumps(info)
            yield item

    def filter_number(self, flight_number):
        number = int(re.sub(r'\D', '', flight_number))
        ST = 9871
        ED = 9889
        if flight_number.startswith('VY') and ST <= number <= ED:
            return False
        return True
