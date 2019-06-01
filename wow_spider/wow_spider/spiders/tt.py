# -*- coding: utf-8 -*-
import scrapy, json, time, csv, os, random, logging, traceback, sys
from utils import dataUtil
from utils import pubUtil
from datetime import datetime, timedelta
from wow_spider.items import WowSpiderItem


class TtSpider(scrapy.Spider):
    name = 'tt'
    allowed_domains = ['https://mobile.tigerair.com.au']
    start_urls = ['https://mobile.tigerair.com.au/book/request/availability']
    version = 1.5
    task = []
    isOK = True
    custom_settings = dict(
        CONCURRENT_REQUESTS=1,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 200,
            # 'wow_spider.middlewares.A4OTokenMiddleware': 300,
        },
        DEFAULT_REQUEST_HEADERS={},
        HEADERS={
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'Connection': 'Keep-Alive',
            'apiver': '18.9.1',
            'Content-Type': 'application/json',
            'Host': 'mobile.tigerair.com.au',
            'User-Agent': 'Dalvik/1.6.0 (Linux; U; Android 4.4.2; MI 6  Build/NMF26X)',
        },
        SEAT=5,
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
                result = pubUtil.getUrl('TT', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
                # dt, dep, to = '2019-01-25', 'SYD', 'PER'
                seat = self.custom_settings.get('SEAT')
                payload = {
                    'currencyCode': 'AUD',
                    'departureDate': dt,
                    'destination': to,
                    'numAdults': seat,
                    'numChildren': 0,
                    'numInfants': 0,
                    'origin': dep,
                    'promoCode': ''
                }
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                meta_data = dict(
                    invalid=invalid,
                    payload=payload,
                )
                headers = self.custom_settings.get('HEADERS')
                # headers['User-Agent'] = random.choice(self.ua_data)[0]
                headers['User-Agent'] = self.ua_construction()
                yield scrapy.Request(self.start_urls[0],
                                     callback=self.parse,
                                     headers=headers,
                                     method='POST',
                                     meta={'meta_data': meta_data},
                                     body=json.dumps(payload),
                                     errback=self.errback)

    def parse(self, response):
        self.isOK = True
        # print('*'*50)
        # print response.text
        try:
            json_dict = json.loads(response.body)
        except:
            # 出现503错误，重新进行请求
            meta_data = response.meta.get('meta_data')
            # print '503 error'
            yield scrapy.Request(self.start_urls[0],
                                 callback=self.parse,
                                 method='POST',
                                 meta={'meta_data': meta_data},
                                 body=json.dumps(meta_data.get('payload')),
                                 errback=self.errback)
            return
        try:
            flight_data = json_dict.get('flights')[0]
        except:
            print 'no airport', response.meta.get('invalid')
            return
        arrAirport = flight_data.get('destination')
        depAirport = flight_data.get('origin')
        currency = flight_data.get('currencyCode')
        flights = flight_data.get('flights')
        # 循环遍历航班
        for flight in flights:
            # 判断中转,之前中转判断有误，增加对sellkey的判断
            sell_Key = flight.get('fares')[0].get('sellKey')
            if sell_Key:
                if len(sell_Key.split('^')) >= 2:
                    # print('is Change')
                    continue
            if flight.get('stops') > 0:
                continue
            carrier = flight.get('carrierCode')
            flightNumber = '%s%s' % (carrier, flight.get('flightNumber'))
            deptime = time.strptime(flight.get('std'), '%Y-%m-%d %H:%M:%S')
            depTime = time.mktime(deptime)
            arrtime = time.strptime(flight.get('sta'), '%Y-%m-%d %H:%M:%S')
            arrTime = time.mktime(arrtime)
            maxSeats = self.custom_settings.get('SEAT')
            isChange = 1
            # 存在两种票价
            fares = flight.get('fares')
            adultPrice, adultTax, netFare, cabin = sys.maxint, 0, 0, 0
            for fare in fares:
                price = fare.get('total')
                if price > adultPrice:
                    continue
                adultPrice = price
                adultTax = fare.get('tax')
                netFare = fare.get('base')
                cabin = fare.get('fareClass')
                info = {'farekey': fare.get('sellKey')}

                #增加套餐价格,先定义价格表
                price_dict = {
                    'Express' : 0,
                }
                for fare in fares:
                    if fare.get('name') == 'Express':
                        price_dict['Express'] = fare.get('total')
                segments = [[price_dict.get('Express'), maxSeats]]
                getTime = time.time()

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
                item['segments'] = json.dumps(segments)
                item['getTime'] = getTime
                item['info'] = json.dumps(info)
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
        inputFile = open(os.path.join('utils', 'TT.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now()
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        for i in range(1, 30):
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
