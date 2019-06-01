# -*- coding: utf-8 -*-
import sys
import time
import json

import scrapy
from jsonpath import jsonpath

from utils.spe_util import vyUtil
from utils import pubUtil, dataUtil
from lmd_spiders.items import LmdSpidersItem


class PnSpider(scrapy.Spider):
    name = 'pn'
    carrier = 'PN'
    allowed_domains = ['app.westair.cn']
    start_urls = 'https://app.westair.cn/flyplus/api/flight/list'
    version = 1.2
    task = []
    isOK = True
    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Host': "app.westair.cn",
            'version': "1",
            'deviceSystemVersion': "12.1",
            'Accept': "*/*",
            'appVersion': "3.0.2",
            'Accept-Language': "zh-Hans-CN;q=1, en-CN;q=0.9, en-US;q=0.8",
            'Accept-Encoding': "br, gzip, deflate",
            'Content-Type': "application/json",
            'deviceId': "75A60468CFA74198",
            'User-Agent': "FlyPlusProject/3.0.2 (iPhone; iOS 12.1; Scale/2.00)",
            'deviceSystem': "iOS",
            'appFrom': "westAirPlus",
            'deviceModel': "iPhone",
            'cache-control': "no-cache"
        },

        CONCURRENT_REQUESTS=1,

        DOWNLOAD_DELAY=2,

        DOWNLOAD_TIMEOUT=10,

        PROXY_TRY_NUM=1,

        DOWNLOADER_MIDDLEWARES={
            'lmd_spiders.middlewares.StatisticsItem': 200,
            'lmd_spiders.middlewares.ProxyMiddleware': 300,
        },

        DEFAULT_DATA={
            # "endCity": "SIN",
            # "beginCity": "CKG",
            # "beginDate": "2019-02-22",
            "inf": "0",
            "cnn": "0",
            "type": "0",
            "sign": "cc7b2df6b2718a888de03334167fe9bb",
            "adt": "3"
        },

        # ITEM_PIPELINES={  # 往测试库添加数据
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },

    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.port_city = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pubUtil.get_task(self.name, 60)
                result = next(result_iter)
            else:
                result = pubUtil.getUrl(self.carrier, 1)
            if not result:
                time.sleep(3)
                continue
            for data in result:
                (dt_st, dep, arr, days) = vyUtil.analysisData(data)
                for i in range(int(days)):
                    dt = vyUtil.get_real_date(dt_st, i)
                    data = dict(
                        beginCity=dep,
                        endCity=arr,
                        beginDate=dt
                    )
                    data.update(self.custom_settings.get('DEFAULT_DATA'))
                    yield scrapy.Request(
                        url=self.start_urls,
                        method="POST",
                        body=json.dumps(data),
                        meta=dict(data=data),
                        dont_filter=True,
                        callback=self.parse,
                        errback=self.errback,
                    )

    def errback(self, failure):
        self.log(failure.value, 40)
        self.isOK = False
        return failure.request

    def parse(self, response):
        data = json.loads(response.body)
        self.isOK = True
        code = data.get('code')
        if '33020' == code:
            self.log('no ticket', 20)
            return
        dt = response.meta.get('data').get('beginDate')
        journeys = jsonpath(data, '$..%s' % dt)[0]
        for journey in journeys:
            dep_airport = journey.get('beginCity')
            arr_airport = journey.get('endCity')
            from_city = self.port_city.get(dep_airport, dep_airport)
            to_city = self.port_city.get(arr_airport, arr_airport)
            fn = journey.get('flightNum')

            dep_time_str = '%s %s' % (journey.get('beginDate'), journey.get('beginDateTime'))
            arr_time_str = '%s %s' % (journey.get('endDate'), journey.get('endDateTime'))
            dep_time = time.mktime(time.strptime(dep_time_str, '%Y-%m-%d %H:%M:%S'))
            arr_time = time.mktime(time.strptime(arr_time_str, '%Y-%m-%d %H:%M:%S'))

            fares = journey.get('ta1')
            low_price = 0
            low_fare = None
            for fare in fares:
                this_price = int(fare.get('flightPrice'))
                if not low_price or (low_price > this_price):
                    low_fare = fare
                    low_price = this_price
            adult_price = low_price
            cabin = low_fare.get('bookingClass')
            seats = low_fare.get('seat')
            if u'充足' == seats:
                seats = 10
            else:
                seats = int(seats)

            item = LmdSpidersItem()
            item.update(dict(
                flightNumber=fn,  # 航班号
                depTime=dep_time,  # 出发时间
                arrTime=arr_time,  # 达到时间
                fromCity=from_city,  # 出发城市
                toCity=to_city,  # 到达城市
                depAirport=dep_airport,  # 出发机场
                arrAirport=arr_airport,  # 到达机场
                currency='CNY',  # 货币种类
                adultPrice=adult_price,  # 成人票价
                adultTax=0,  # 税价
                netFare=adult_price,  # 净票价
                maxSeats=seats,  # 可预定座位数
                cabin=cabin,  # 舱位
                carrier=fn[:2],  # 航空公司
                isChange=1,  # 是否为中转 1.直达2.中转
                segments="[]",  # 中转时的各个航班信息
                getTime=time.time(),
            ))
            yield item
