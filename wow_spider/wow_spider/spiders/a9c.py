# -*- coding: utf-8 -*-
import scrapy, json, time, csv, os, random, logging, traceback, sys
from utils import dataUtil
from utils import pubUtil
from datetime import datetime, timedelta
from wow_spider.items import WowSpiderItem


class A9cSpider(scrapy.Spider):
    name = '9c'
    allowed_domains = ['ch.com']
    start_urls = ['https://flights.ch.com/Flights/SearchByTime']
    version = 1.2
    task = []
    isOK = True
    custom_settings = dict(
        CONCURRENT_REQUESTS=1,
        PROXY_TRY_NUM=1,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            # 'wow_spider.middlewares.ProxyMiddleware': 200,
            'wow_spider.middlewares.A9CJSMiddleware': 300,
        },
        DEFAULT_REQUEST_HEADERS={},
        HEADERS={
            'Origin': 'https://flights.ch.com',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.96 Safari/537.36',
            'Connection': 'keep-alive',
            'X-Requested-With': 'XMLHttpRequest',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': 'acw_sc__v2=5c67ab816035c41f32a33b633d82102379f2eb75',
        },
        SEAT=1,
        # CURRENCY_CACHE={
        #     u'$': u'AUD',
        # },


    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        result_iter = None
        result = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter or not result:
                    result_iter = self.get_task()
                result = next(result_iter)
            else:
                result = pubUtil.getUrl('9C', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
            # for i in range(10):
            #     dt, dep, to = '2019-02-25', 'SJW', 'TPE'
            #     print(dt, dep, to)
                seat = self.custom_settings.get('SEAT')
                payload = {
                    'Arrival': to,
                    'IsIJFlight': 'false',
                    'CabinActId': 'null',
                    'SeatsNum': seat,
                    'Currency': '0',
                    'IsLittleGroupFlight': 'false',
                    'ReturnDate': 'null',
                    'Departure': dep,
                    'IsUM': 'false',
                    'IsBg': 'false',
                    'IsJC': 'false',
                    'Active9s': '',
                    'IsShowTaxprice': 'false',
                    'DepartureDate': dt,
                    'isdisplayold': 'false',
                    'ActId': '0',
                    'IfRet': 'false',
                    'IsEmployee': 'false',
                    'SType': '0'
                }
                form = ''
                for b in payload:
                    form = form + b + '=' + str(payload.get(b)) + '&'
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                meta_data = dict(
                    invalid=invalid,
                    form=form,
                )
                yield scrapy.Request(self.start_urls[0],
                                     callback=self.parse,
                                     headers=self.custom_settings.get('HEADERS'),
                                     method='POST',
                                     meta={'meta_data': meta_data},
                                     body=form,
                                     errback=self.errback)

    def parse(self, response):
        self.isOK = True
        # print('*'*50)
        # print response.text
        # return
        try:
            json_dict = json.loads(response.body)
        except:
            print response.text
            # 出现503错误，重新进行请求
            # meta_data = response.meta.get('meta_data')
            # print '503 error'
            # yield scrapy.Request(self.start_urls[0],
            #                      callback=self.parse,
            #                      method='POST',
            #                      meta={'meta_data': meta_data},
            #                      body=json.dumps(meta_data.get('payload')),
            #                      errback=self.errback)
            return
        flights = json_dict.get('Route')
        if not flights:
            return
        # 循环遍历航班
        for flight in flights:
            # 判断中转
            if len(flight) > 1:
                continue
            flight_data = flight[0]
            depAirport = flight_data.get('DepartureAirportCode')
            arrAirport = flight_data.get('ArrivalAirportCode')
            # 取不到货币，暂定CNY
            currency = 'CNY'
            flightNumber = flight_data.get('No')
            carrier = flightNumber[:2]
            deptime = time.strptime(flight_data.get('DepartureTime'), '%Y-%m-%d %H:%M:%S')
            depTime = time.mktime(deptime)
            arrtime = time.strptime(flight_data.get('ArrivalTime'), '%Y-%m-%d %H:%M:%S')
            arrTime = time.mktime(arrtime)
            isChange = 1
            getTime = time.time()
            cabin, adultTax, adultPrice, maxSeats, netFare = 'X', 0, 0, 0, 0
            for flight_price in flight_data.get('AircraftCabins'):
                cabin = flight_price.get('CabinLevel')
                price_and_seat = flight_price.get('AircraftCabinInfos')[0]
                adultTax = price_and_seat.get('AirportConstructionFees') + price_and_seat.get('FuelSurcharge') + price_and_seat.get('OtherFees')
                netFare = price_and_seat.get('Price')
                adultPrice = adultTax + netFare
                maxSeats = price_and_seat.get('Remain')
                if maxSeats != -1:
                    break

            item = WowSpiderItem()
            item['flightNumber'] = flightNumber
            item['depTime'] = depTime
            item['arrTime'] = arrTime
            item['fromCity'] = self.portCitys.get(depAirport, depAirport)
            item['toCity'] = self.portCitys.get(arrAirport, arrAirport)
            item['depAirport'] = depAirport
            item['arrAirport'] = arrAirport
            item['currency'] = currency
            item['adultPrice'] = adultPrice
            item['adultTax'] = adultTax
            item['netFare'] = netFare
            item['maxSeats'] = maxSeats
            item['cabin'] = cabin
            item['carrier'] = carrier
            item['isChange'] = isChange
            item['segments'] = json.dumps([])
            item['getTime'] = getTime
            item['info'] = json.dumps([])
            yield item
            # print(item)

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-'*40)
        print(failure.value)
        # yield failure.request




    def get_task(self):
        print "local task"
        inputFile = open(os.path.join('utils', '9C.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now()
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        for i in range(6, 30):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y%m%d')
            for data in datas:
                if not data or not len(data):
                    continue
                # yield (data[0], data[1], _dt)
                yield ['%s-%s:%s:1' % (data[0], data[1], _dt)]

    def ua_construction(self):
        # 模板样式
        ua_example = 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; LGL51AL Build/LMY47V)'
        android_list = [
            '8.0', '7.1.1', '7.0', '6.0.1',
            '6.0', '5.1.1', '5.1', '5.0.2',
            '5.0.1', '5.0.0', '4.4.4', '4.4.3',
            '4.4.2', '4.4.1', '4.4',
        ]
        phone_list = [
            'SM-G925F', 'Lenovo K8 Note', 'GT-I9300', 'SM-G710', 'vivo-Y18L', '0PCV1',
            'HTC-Desire', 'GT-I9105P', 'GT-I8200', 'Z930L', 'VS870', 'Lenovo-A328',
            'LG-D165AR', 'Nexus-4', 'Nexus-5', 'SM-G313MU', 'vivo-Y23L', 'Redmi-Note',
        ]
        build_list = [
            'LRX22G', 'LRX21M', 'LMY47V', 'LVY48F', 'LRX21Y', 'KTU84P',
            'JOP40D', 'KOT49H', 'KTU84M', 'KOT49I', 'JWR67B', 'JSS15J',
            'JDQ39', 'JZO54K', 'IMM76B', 'MMB29V', 'LMY47D', 'MHC19Q',
        ]
        ua = 'Dalvik/2.1.0 (Linux; U; Android %s; %s Build/%s)'%\
             (random.choice(android_list), random.choice(phone_list), random.choice(build_list))
        return ua
