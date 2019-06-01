# -*- coding: utf-8 -*-
import scrapy,json,time,csv,os,random,logging,traceback
from utils import dataUtil
from utils import pubUtil
from datetime import datetime, timedelta
from wow_spider.items import WowSpiderItem


class G9Spider(scrapy.Spider):
    name = 'g9'
    allowed_domains = ['airarabia.com']
    start_urls = ['https://androidapi.airarabia.com/mobile-engine/api/flightSearch']
    version = 1.2
    task = []
    isOK = False
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 200,
            # 'wow_spider.middlewares.XQSessionMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=15,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=5,
        COOKIES_ENABLED=False,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=8,
        # ITEM_PIPELINES = {
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS={
            'Content-Type': 'application/json; charset=UTF-8',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'okhttp/3.10.0',
            'Referer' : 'https://androidapi.airarabia.com/mobile-engine/api/flightSearch',
        },
        SEAT=3,

    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl('G9', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
            # # for i in range(1):
            # for data in self.get_task():
            #     dep, to, dt = data
            #     dt,dep,to = '2018-10-16','SHJ','DMM'
                seat = self.custom_settings.get('SEAT')
                payload = {
                    "dataModel": {
                        "app": {
                            "apiKey": "api_key",
                            "appVersion": "4.0.3",
                            "language": "en",
                            "os": "android"
                        },
                        "isReturn": False,
                        "journeyInfo": [{
                            "departureDateTime": "%sT00:00:00"%dt,
                            "departureVariance": 0,
                            "destination": to,
                            "destinationCity": False,
                            "origin": dep,
                            "originCity": False
                        }],
                        "preferences": {
                            "cabinClass": "Y",
                            "currency": "USD",
                            "logicalCabinClass": "Y",
                            "promotion": {
                                "code": "",
                                "type": "PROMO_CODE"
                            }
                        },
                        "travellerQuantity": {
                            "adultCount": seat,
                            "childCount": "0",
                            "infantCount": "0"
                        }
                    }
                }
                body = json.dumps(payload)
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                meta_data = dict(
                    invalid=invalid,
                    payload=body,
                    aaa=(dep, to, dt),
                    flight_time=dt
                )
                yield scrapy.Request(self.start_urls[0],
                                     callback=self.parse,
                                     method='POST',
                                     headers=self.custom_settings.get('HEADERS'),
                                     meta={'meta_data': meta_data},
                                     body=body,
                                     errback=self.errback
                                     )

    def parse(self, response):
        # print(response.text)
        # print('1' * 66)
        self.isOK = True
        if response.text == 'Service Unavailable, Rate limit reached, No Direct Access.':
            self.isOK = False
            # print(response.text)
            # print(response.status)
            # print(response.request.cookies)
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=response.meta.get('meta_data').get('body'),
                                 callback=self.parse,
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback
                                 )
            return
        try:
            json_dict = json.loads(response.body)
        except:
            print(response.text)
            print(response.status)
            traceback.print_exc()
        if json_dict.get('message').get('code') == 400:
            self.isOK = False
            print(response.text)
            print(response.status)
            # print(response.request.cookies)
            # print(response.meta.get('meta_data').get('aaa'))
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=response.meta.get('meta_data').get('body'),
                                 callback=self.parse,
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback
                                 )
            return
        if json_dict.get('message').get('code') == 500:
            # print(response.text)
            # print(response.meta.get('meta_data').get('aaa'))
            return
        # try:
        availableOptions = json_dict.get('data').get('originDestinationResponse')[0].get('availableOptions')
        # except:
        #     traceback.print_exc()
        #     print(response.text)
        #     print(response.status_code)
        currency = json_dict.get('data').get('currency')
        print('6'*66)
        # print(response.request.cookies)
        # 这个请求会显示七天的航班，在这个列表里
        for flight in availableOptions:
            # 判断是否是中转
            flight_segments = flight.get('segments')
            if len(flight_segments) > 1:
                print('is change')
                continue
            flight_segment = flight_segments[0]
            carrier = flight_segment.get('carrierCode')
            flightNumber = flight_segment.get('filghtDesignator')
            deptime_tuple = time.strptime(flight_segment.get('departureDateTime').get('local'), '%Y-%m-%dT%H:%M:%S')
            depTime = time.mktime(deptime_tuple)
            arrtime_tuple = time.strptime(flight_segment.get('arrivalDateTime').get('local'), '%Y-%m-%dT%H:%M:%S')
            arrTime = time.mktime(arrtime_tuple)
            depAirport = flight.get('originAirportCode')
            arrAirport = flight.get('destinationAirportCode')
            availableFare = flight.get('availableFareClasses')
            if not availableFare:
                maxSeats = 0
                adultPrice = 0
            else:
                maxSeats = availableFare[0].get('availableSeats')
                if maxSeats== -1:
                    maxSeats = 9
                adultPrice = availableFare[0].get('price') * 1.03
            adultTax=0
            netFare = adultPrice - adultTax

            isChange = 1
            cabin = 'X'
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
            item['segments'] = '[]'
            item['getTime'] = getTime
            yield item

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        # print('-' * 40)
        # print(failure.value)
        yield failure.request

    def get_task(self):
        inputFile = open(os.path.join('utils', 'G9.csv'))
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now()
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 1
        add_num = random.randint(1, 20)
        for i in range(add_num, 30, days):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y-%m-%d')
            for data in datas:
                if not data or not len(data):
                    continue
                yield (data[0], data[1], _dt)