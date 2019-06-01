# -*- coding: utf-8 -*-
import re
import time
import json
import urllib
from datetime import datetime
from datetime import timedelta

import scrapy
from jsonpath import jsonpath

from utils import pub_util
from utils import data_util
from example.items import ExampleItem


class F3Spider(scrapy.Spider):
    name = 'f3'
    allowed_domains = ['book.flyadeal.com']
    start_url = 'https://book.flyadeal.com/api/flights?'
    token_url = 'https://book.flyadeal.com/api/session'
    version = 1.2
    task = []
    seats = 3
    is_ok = True
    custom_settings = dict(

        DEFAULT_REQUEST_HEADERS={
            'accept': "application/json, text/plain, */*",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/69.0.3497.100 Safari/537.36",
            'referer': "https://book.flyadeal.com/",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cache-control': "no-cache",
        },

        CONCURRENT_REQUESTS=8,

        DOWNLOADER_MIDDLEWARES={
            'example.middlewares.StatisticsItem': 200,
            'example.middlewares.F3TokenMiddleware': 300,
        },

        DEFAULT_PARAMS={  # 参数包括
            # "availabilityRequests[0].departureStation": "TUU",
            # "availabilityRequests[0].arrivalStation": "RUH",
            # "availabilityRequests[0].beginDate": "2018-11-06",
            # "availabilityRequests[0].endDate": "2018-11-06",
            "availabilityRequests[0].paxTypeCounts[0].paxTypeCode": "ADT",
            "availabilityRequests[0].paxTypeCounts[0].paxCount": str(seats),
            "availabilityRequests[0].currencyCode": "SAR",
            "availabilityRequests[0].paxResidentCountry": "SA",
            "availabilityRequests[0].promotionCode": ""
        },

        # ITEM_PIPELINES={
        #     'example.pipelines.ExamplePipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.port_city = data_util.get_port_city()

    def start_requests(self):
        permins = 0
        self.log(pub_util.heartbeat(self.host_name, self.name, self.num, permins, self.version), 20)
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pub_util.get_task(self.name, days=10)
                result = next(result_iter)
            else:
                result = pub_util.get_url(self.name, 1)
            if not result:
                self.log('get task error', 30)
                time.sleep(10)
                continue
            for data in result:

                # 处理任务 data JED-AHB:20181218:1
                dt, dep, arr, days = data_util.parse_data(data)
                # print data
                # print dep, arr, dt, days
                this_day = datetime.strptime(dt, '%Y%m%d')
                for diff_day in range(int(days)):
                    dt_format = (this_day + timedelta(days=diff_day)).strftime('%Y-%m-%d')

                    params = {  # 可变参数
                        "availabilityRequests[0].departureStation": dep,
                        "availabilityRequests[0].arrivalStation": arr,
                        "availabilityRequests[0].beginDate": dt_format,
                        "availabilityRequests[0].endDate": dt_format,
                    }
                    params.update(self.custom_settings.get('DEFAULT_PARAMS'))
                    url = self.start_url + urllib.urlencode(params)
                    yield scrapy.Request(
                        url=url,
                        dont_filter=True,
                        callback=self.parse,
                        errback=self.err_back,
                    )

    def err_back(self, failure):
        self.log(failure.value, 40)
        self.log(failure.request.meta.get('proxy'))
        self.is_ok = False
        return failure.request

    def parse(self, response):
        try:
            data_dict = json.loads(response.body)
        except Exception as e:
            print(response.body)
            print(response.status)
            print(e)
            return
        self.is_ok = True
        fares = data_dict.get('fares')
        journeys = jsonpath(data_dict, '$..journeys')[0]
        for journey in journeys:
            segments = journey.get('segments')
            if len(segments) > 1:
                continue
            journey_key = journey.get('journeySellKey')
            important = filter(lambda x: x, re.split(r'~[~|\s]*', journey_key))
            carrier, fn_no, dep_port, dep_date, arr_port, arr_date = important
            flight_number = carrier + fn_no
            dep_time = time.mktime(time.strptime(dep_date, '%m/%d/%Y %H:%M'))
            arr_time = time.mktime(time.strptime(arr_date, '%m/%d/%Y %H:%M'))
            available_fares = jsonpath(segments, '$..availableFares')[0]
            dep_city = self.port_city.get(dep_port, dep_port)
            arr_city = self.port_city.get(arr_port, arr_port)

            # 获取有座位的最低价和套餐价格
            fare_index_low = None
            dif_pack = []
            seats = 0
            for i, available_fare in enumerate(available_fares):
                fare_index_temp = available_fare.get('fareIndex')
                if fare_index_low is None:
                    fare_index_low = fare_index_temp
                    seats_str = available_fare.get('availableCount')
                    seats = 9 if seats_str == 32767 else seats_str
                if i:
                    fare_temp = fares[fare_index_temp]
                    price_temp = jsonpath(fare_temp, '$..amount')[0]
                    seats_temp_str = available_fare.get('availableCount')
                    seats_temp = 9 if seats_temp_str == 32767 else seats_temp_str
                    dif_pack.append([price_temp, seats_temp])

            fare = fares[fare_index_low]
            cabin = fare.get('classOfService')
            price = jsonpath(fare, '$..amount')[0]
            net_fare = price
            adult_tax = 0
            currency = jsonpath(fare, '$..currencyCode')[0]

            item = ExampleItem()
            item.update(dict(
                flight_number=flight_number,
                dep_time=dep_time,
                arr_time=arr_time,
                dep_port=dep_port,
                arr_port=arr_port,
                currency=currency,
                adult_price=price,
                adult_tax=adult_tax,
                net_fare=net_fare,
                max_seats=seats,
                cabin=cabin,
                carrier=carrier,
                is_change=1,
                segments=json.dumps(dif_pack),
                get_time=time.time(),
                from_city=dep_city,
                to_city=arr_city,
                info='',
            ))
            yield item
