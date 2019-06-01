# -*- coding: utf-8 -*-
import scrapy,json
from datetime import datetime, timedelta
import csv, os,time,re, sys,logging
from jsonpath import jsonpath
from utils import dataUtil
from utils import pubUtil
from wow_spider.items import WowSpiderItem



class KcSpider(scrapy.Spider):
    name = 'kc'
    task = []
    allowed_domains = ['airastana.com']
    start_urls = ['http://airastana.com/']
    version = 1.0
    isOK = True,
    isToken_cookie = True,
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            # 'lamudatech_dev.middlewares.LamudatechDevDownloaderMiddleware': 543,
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.KCCookieMiddleware': 300,
            # 'wow_spider.middlewares.ProxyMiddleware': 200,

        },

        HTTPERROR_ALLOWED_CODES=[302],
        token_url = ['https://airastana.com/global/en-us/'],
        cookie_url = ['https://airastana.com/global/en-us/'],
        sessionID_url = 'https://airastana.com/DesktopModules/AirAstana/AirAstana.Dnn.Components/GeneralBookingWs.asmx/FindFlight',
        data_url='https://booking.airastana.com/plnext/AirAstana2DX/Override.action',

        start_headers={
            'content-type': 'application/json; charset=UTF-8',
            'referer': 'https://airastana.com/chn/zh-CN',
            'accept-language': 'zh-CN,zh;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
            'Cookie':'',
        },

        # LOG_LEVEL = "DEBUG",

        data_headers = {
        'Origin':'https://airastana.com',
        'Content-Type':'application/x-www-form-urlencoded',
        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Safari/537.36',
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
        'Referer':'https://airastana.com/chn/zh-CN',
        'Accept-Language':'zh-CN,zh;q=0.9',
        'Cookie':'',
        },
        DOWNLOAD_TIMEOUT=30,
        # COOKIES_ENABLED=False,
        INVALID_TIME=45,
        PROXY_TRY_NUM=8,
        CONCURRENT_REQUESTS=32,
        ITEM_PIPELINES = {
            'wow_spider.pipelines.LmdSpidersPipeline': 300,
        }

    )


    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()


    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name,self.name,self.num,permins,self.version))
        while True:
            result = pubUtil.getUrl('KC', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, arr) = pubUtil.analysisData(data)
                dt = re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\3.\2.\1', dt)
                # print(dt)
                # dt = time.strftime('%d.%m.%Y',dt)
                print(dep, arr, dt)
                payload = {
                    'captchaResponse': '',
                    'pReturnDateStr': '',
                    'pFlightDateStr': dt,
                    'pRequest': {
                         'TwoWayRoute': 'false',
                         'DateAreFlexible': 'true',
                         'Origin': dep,
                         'Destination': arr,
                         'Bookingclass': 'ECO',
                         'Adult': '3',
                         'Child': '0',
                         'Infant': '0',
                         'Resident': 'false'
                    },
                }
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': arr,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                meta_data = dict(
                    invalid=invalid,
                    payload=payload
                )
                yield scrapy.Request(self.custom_settings.get('sessionID_url'),
                                     callback=self.data_requests,method='POST',
                                     headers=self.custom_settings.get('start_headers'),
                                     meta={'meta_data': meta_data},
                                     body=json.dumps(payload),
                                     errback=self.errback)


    def data_requests(self,response):
        res = None
        message = None

        try:
            res = json.loads(response.text).get('d')
            message = res.split('"')[5]
            # print(message)
        except:
            self.log('data_requests: get_d error', 40)
            print('session ID error')
            print(response.text)
            meta_data = response.meta['meta_data']
            payload = response.meta['meta_data'].get('payload')
            # self.isToken_cookie = False
            # self.isOK = False

            yield scrapy.Request(self.custom_settings.get('sessionID_url'),
                                 callback=self.data_requests,
                                 method='POST',
                                 headers=self.custom_settings.get('start_headers'),
                                 meta={'meta_data': meta_data},
                                 body=json.dumps(payload),
                                 errback=self.errback)
        # self.isToken_cookie = True
        self.isOK = True
        invalid = response.meta.get('meta_data').get('invalid')
        body = 'SITE=CAZICNEW&LANGUAGE=CN&EMBEDDED_TRANSACTION=FlexPricerAvailability&ENCT=1&ENC=%s' % message
        yield scrapy.Request(self.custom_settings.get('data_url'),
                             callback=self.parse,
                             method='POST',
                             headers=self.custom_settings.get('data_headers'),
                             meta={'invalid': invalid},
                             body=body,
                             errback=self.errback)



    def parse(self, response):
        # print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++====')
        self.isOK = True
        parrten = re.compile(r'config\s:\s([\s\S]*), pageEngine : pageEngine')
        data = parrten.findall(response.text)
        if not len(data):
            print('data not')
            print('response:'+ response.text)
            # print(response.text)
            return
        data = data[0].strip('\n ')
        dict_data = json.loads(data)
        Availability = jsonpath(dict_data, '$..Availability')
        if not Availability:
            self.task.append(response.meta.get('invalid'))
            return

        # 航班列表
        flight_list = jsonpath(Availability[0], '$..proposedFlightsGroup')[0]
        # 获取当天每个航班信息
        for flight_data in flight_list:
            # 是否中转，不确定后期调整
            if len(flight_data.get('segments')) > 1:
                continue
            # 航班号
            flightNumber = jsonpath(flight_data, '$..airline')[0].get('code') + jsonpath(flight_data, '$..flightNumber')[0]
            deptime = time.strptime(jsonpath(flight_data, '$..beginDate')[0], '%b %d, %Y %I:%M:%S %p')
            # 出发时间
            depTime = time.mktime(deptime)
            arrtime = time.strptime(jsonpath(flight_data, '$..endDate')[0], '%b %d, %Y %I:%M:%S %p')
            # 到达时间
            arrTime = time.mktime(arrtime)
            # 出发城市代码
            fromCity = jsonpath(flight_data, '$..beginLocation')[0].get('cityCode')
            # 到达城市代码
            toCity = jsonpath(flight_data, '$..endLocation')[0].get('cityCode')
            # 出发机场代码
            depAirport = jsonpath(flight_data, '$..beginLocation')[0].get('locationCode')
            # 到达机场代码
            arrAirport = jsonpath(flight_data, '$..endLocation')[0].get('locationCode')
            # 货币种类
            currency = jsonpath(Availability, '$..currencyBean')[0].get('code')

            final_price, adultPrice, adultTax, netFare = sys.maxint,0,0,0
            maxSeats, cabin = 0, ''
            # 分类价格,获取当天每个航班座位数对比
            flight_id = flight_data.get('proposedBoundId')
            for recommendation in jsonpath(Availability,'$..recommendationList')[0]:
                # 价格
                price = jsonpath(recommendation, '$..boundAmount')[0]
                price_current = price.get('totalAmount')
                if price_current >= final_price:
                    continue
                for flightGroup in jsonpath(recommendation, '$..flightGroupList')[0]:
                    # 座位数,舱位
                    if flightGroup.get('flightId') == flight_id:
                        # 含税价
                        adultPrice = price.get('totalAmount') / 3
                        final_price = price_current
                        # 税价
                        adultTax = price.get('tax') / 3
                        # 净票价
                        netFare = price.get('amountWithoutTaxAndFee') / 3
                        maxSeats = flightGroup.get('numberOfSeatsLeft')
                        cabin = flightGroup.get('rbd')

            # 航司二字码
            carrier = jsonpath(flight_data, '$..airline')[0].get('code')
            isChange = len(flight_data.get('segments'))
            flightTime = jsonpath(flight_data, '$..flightTime')[0]
            # 航段信息
            segments = dict(
                flightNumber=flightNumber,
                aircraftType=jsonpath(flight_data, '$..equipment')[0].get('code'),
                number=1,
                departureTime=time.strftime('%Y-%m-%d %H:%M:%S', deptime),
                destinationTime=time.strftime('%Y-%m-%d %H:%M:%S', arrtime),
                airline=carrier,
                dep=depAirport,
                dest=arrAirport,
                seats=maxSeats,
                duration='%02d:%02d' % (flightTime / 60000, flightTime % 60000),
                depTerminal=''
            )
            getTime = time.time()

            item = WowSpiderItem()
            item['flightNumber'] = flightNumber
            item['depTime'] = depTime
            item['arrTime'] = arrTime
            item['fromCity'] = self.portCitys.get(depAirport, fromCity)
            item['toCity'] = self.portCitys.get(arrAirport,toCity)
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
            item['segments'] = segments
            item['getTime'] = getTime

            yield item





    def errback(self, failure):
        print('------------------------------------------------')
        self.log(failure.value, 40)
        self.isOK = False
        # self.isToken_cookie = False
        return failure.request





    def get_task(self):
        inputFile = open(os.path.join('utils', 'KC.csv'))
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now()
        #倒序输出
        datas = datas[::-1]
        for i in range(8,9):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%d.%m.%Y')
            for data in datas:
                if not data or not len(data):
                    continue
                yield (data[0], data[1], _dt)