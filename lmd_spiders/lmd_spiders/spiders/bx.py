# -*- coding: utf-8 -*-
import re
import json
import time

import scrapy
from jsonpath import jsonpath

from utils import pubUtil, dataUtil
from utils.spe_util import vyUtil
from lmd_spiders.items import LmdSpidersItem


class BxSpider(scrapy.Spider):
    name = 'bx'
    allowed_domains = ['airbusan.com']
    start_url = 'https://cn.airbusan.com/web/bookingApi/flightsAvail'
    version = 1.3
    carrier = 'BX'
    task = []
    is_ok = True

    custom_settings = dict(
        PAY_LOAD=dict(
            bookingCategory='Individual',
            focYn='N',
            tripType='OW',
            # depCity1='PUS',
            # arrCity1='GMP',
            # depDate1='2018-12-27',
            paxCountCorp='0',
            paxCountAd='3',
            paxCountCh='0',
            paxCountIn='0'
        ),

        DEFAULT_REQUEST_HEADERS={
            'accept': "application/json, text/javascript, */*; q=0.01",
            'origin': "https://cn.airbusan.com",
            'x-requested-with': "XMLHttpRequest",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
            'content-type': "application/x-www-form-urlencoded",
            'referer': "https://cn.airbusan.com/web/individual/booking/flightsAvail",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cache-control': "no-cache",
        },

        CONCURRENT_REQUESTS=4,

        COOKIES_ENABLED=False,

        DOWNLOADER_MIDDLEWARES={
            'lmd_spiders.middlewares.StatisticsItem': 200,
            'lmd_spiders.middlewares.BxProxyMiddleware': 300,
        },

        # # 测试库
        # ITEM_PIPELINES={
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # }
    )

    def __init__(self, *args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)
        self.port_city = dataUtil.get_port_city()

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
                time.sleep(3)
                continue
            for data in result:
                (dt_st, dep, arr, days) = vyUtil.analysisData(data)
                for i in range(int(days)):
                    dt = vyUtil.get_real_date(dt_st, i)
                    pay_load = dict(
                        depCity1=dep,
                        arrCity1=arr,
                        depDate1=dt,
                    )
                    pay_load.update(self.custom_settings.get('PAY_LOAD'))
                    yield scrapy.FormRequest(
                        self.start_url,
                        formdata=pay_load,
                        meta={'payload': pay_load},
                        callback=self.parse,
                        dont_filter=True,
                        errback=self.err_back,
                    )

    def err_back(self, failure):
        # self.log('%s ip: %s' % (failure.value, failure.request.meta.get('proxy')), 40)
        self.is_ok = False
        return failure.request

    def parse(self, response):
        self.is_ok = True
        try:
            result = json.loads(response.text)
        except Exception as e:
            print(e)
            print(response.text)
            print(response.status)
            return

        try:
            tax_ad = jsonpath(result, '$..taxAd')[0]
        except Exception as e:
            self.log(e, 20)
            params = result.get('param')
            if not params:
                params = response.meta.get('payload')
            dep = params.get('depCity1')
            arr = params.get('arrCity1')
            date = params.get('depDate1')
            self.log('%s->%s on %s no data' % (dep, arr, date), 20)
            return
        fuel_ad = jsonpath(result, '$..fuelAd')[0]
        adult_tax = tax_ad + fuel_ad
        # 航班
        list_fare = result.get('listItineraryFare')
        for item_fare in list_fare:
            dep_airport = item_fare.get('depCity')
            arr_airport = item_fare.get('arrCity')
            from_city = self.port_city.get(dep_airport, dep_airport)
            to_city = self.port_city.get(arr_airport, arr_airport)
            list_flight = item_fare.get('listFlight')
            for flight in list_flight:
                dep_str = flight.get('depDate') + flight.get('depTime')
                arr_str = flight.get('arrDate') + flight.get('arrTime')
                dep_time = time.mktime(time.strptime(dep_str, '%Y%m%d%H%M'))
                arr_time = time.mktime(time.strptime(arr_str, '%Y%m%d%H%M'))
                c, n = re.match(r'([A-Z]+)(\d+)', flight.get('flightNo')).groups()
                flight_number = c + n.lstrip('0')

                net_fare = 0
                cabin = ''
                currency = ''
                seats = 0
                # 获取最低价
                list_cls = flight.get('listCls')
                for cl in list_cls:
                    # 忽略1+1 EVENT促销机票
                    if cl.get('cls') == 'F':
                        # print '#' * 66, '1+1'
                        continue
                    flag_fare = cl.get('priceAd')
                    if not net_fare or net_fare > flag_fare:
                        net_fare = flag_fare
                        cabin = cl.get('cls')
                        currency = cl.get('currency')
                        seats = cl.get('avail')

                item = LmdSpidersItem()
                item.update(dict(
                    flightNumber=flight_number,  # 航班号
                    depTime=dep_time,  # 出发时间
                    arrTime=arr_time,  # 达到时间
                    fromCity=from_city,  # 出发城市
                    toCity=to_city,  # 到达城市
                    depAirport=dep_airport,  # 出发机场
                    arrAirport=arr_airport,  # 到达机场
                    currency=currency,  # 货币种类
                    adultPrice=net_fare + adult_tax,  # 成人票价
                    adultTax=adult_tax,  # 税价
                    netFare=net_fare,  # 净票价
                    maxSeats=seats,  # 可预定座位数
                    cabin=cabin,  # 舱位
                    carrier=flight_number[:2],  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="[]",  # 中转时的各个航班信息
                    getTime=time.time(),
                ))

                yield item
