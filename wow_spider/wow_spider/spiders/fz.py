# -*- coding: utf-8 -*-
import scrapy,json,time,csv,os,random,logging,sys,traceback
from jsonpath import jsonpath
from utils import dataUtil
from utils import pubUtil
from datetime import datetime, timedelta
from wow_spider.items import WowSpiderItem


class FzSpider(scrapy.Spider):
    name = 'fz'
    allowed_domains = ['flydubai.com']
    start_urls = ['https://flights1.flydubai.com/api/flights/1']
    version = 1.3
    task = []
    isOK = True
    custom_settings = dict(
        CONCURRENT_REQUESTS=8,
        SEAT=4,
        DURATION=7,
        DOWNLOAD_TIMEOUT=30,
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            # 'wow_spider.middlewares.MMProxyMiddleware': 200,
            # 'wow_spider.middlewares.a5JtokenMiddleware': 300,

        },
        CLOSESPIDER_TIMEOUT=0,
        # ITEM_PIPELINES = {
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS = {
        'accept': "application/json, text/plain, */*",
        'origin': "https://flights1.flydubai.com",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        'content-type': "application/json;charset=UTF-8",
        'referer': "https://flights1.flydubai.com/en/results/ow/a1/DXB_AMD/20180913?isOriginMetro=true&isDestMetro=false&pm=cash",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        'cookie': "incap_ses_460_886152=JhxHZw4zcAC+4xjExUBiBhn3jVsAAAAAuiZP9hBkdIT+O9EavIYTqg=="
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
            result = pubUtil.getUrl('FZ', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
            # for data in self.get_task():
            #     dep, to, dt = data
            #     dt,dep,to= '2018-09-13','DXB','BEY'
                dt_change = datetime.strptime(dt,'%Y-%m-%d').strftime('%m/%d/%Y')
                print(dep, to, dt)
                seat = self.custom_settings.get('SEAT')
                payload = {
                    "journeyType": "ow",
                    "isOriginMetro": False,
                    "isDestMetro": False,
                    "variant": "0",
                    "searchCriteria": [{
                        "origin": dep,
                        "dest":to,
                        "originDesc": "",
                        "destDesc": "",
                        "isOriginMetro": False,
                        "isDestMetro": False,
                        "direction": "outBound",
                        "date": "%s 12:00 AM"%dt_change
                    }],
                    "paxInfo": {
                        "adultCount": seat,
                        "infantCount": 0,
                        "childCount": 0
                    }
                }
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                body=json.dumps(payload)
                meta_data = dict(
                    invalid=invalid,
                    payload=body,
                    aaa = (dep, to, dt)
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
        data = json.loads(response.body)
        try:
            flights = data.get('segments')[0].get('flights')
        except:
            # self.task.append(response.meta.get('invalid'))
            # print(response.text)
            # traceback.print_exc()
            print('6' * 66)
            # print(response.meta.get('meta_data').get('aaa'))
            # print('6' * 66)
            # meta_data = response.meta.get('meta_data')
            # yield scrapy.Request(self.start_urls[0],
            #                      callback=self.parse,
            #                      method='POST',
            #                      headers=self.custom_settings.get('HEADERS'),
            #                      meta={'meta_data': meta_data},
            #                      body=meta_data.get('payload'),
            #                      errback=self.errback
            #                      )
            return
        #判断是否无航班
        if not flights:
            print('No flight to day')
            # print('2'*66)
            self.task.append(response.meta.get('meta_data').get('invalid'))
            return
        # print(len(flights))
        # print(response.text)
        for flight in flights:
            #先判断是否中转
            legs = flight.get('legs')
            if len(flight.get('stops')) > 0 or len(legs) > 1:
                print('is change:%s'%len(flight.get('stops')) )
                # print(len(legs)  )
                continue
            # print('---'*20)
            leg =legs[0]
            carrier = leg.get('operatingCarrier')
            flightNumber = '%s%s' % (carrier, leg.get('marketingFlightNum'))
            dep_tupletime = time.strptime(leg.get('departureDate'), '%Y-%m-%dT%H:%M:%S')
            depTime = time.mktime(dep_tupletime)
            arr_tupletime = time.strptime(leg.get('arrivalDate'), '%Y-%m-%dT%H:%M:%S')
            arrTime = time.mktime(arr_tupletime)
            duration = leg.get('flightDuration')
            depAirport = leg.get('origin')
            arrAirport = leg.get('destination')
            aircraftType = leg.get('equipmentType')

            fareTypes = flight.get('fareTypes')
            final_price = sys.maxint
            fareType = {}
            for fareType_data in fareTypes:
                try:
                    adultPrice = float(jsonpath(fareType_data,'$..adultFarePerPax')[0].replace(',',''))
                except:
                    # traceback.print_exc()
                    # self.task.append(response.meta.get('meta_data').get('invalid'))
                    continue
                if adultPrice >= final_price:
                    continue
                final_price = adultPrice
                fareType =fareType_data
            adultPrice = final_price
            if not fareType:
                # print('1'*66)
                self.task.append(response.meta.get('meta_data').get('invalid'))
                continue
            currency = jsonpath(fareType,'$..currencyCode')[0]
            adultTax = float(jsonpath(fareType,'$..taxPerPax')[0].replace(',',''))
            netFare = float(jsonpath(fareType,'$..baseAdultFarePerPax')[0].replace(',',''))
            cabin = jsonpath(fareType,'$..fareClass')[0]
            #目前暂未发现座位,使用请求的座位
            maxSeats = self.custom_settings.get('SEAT')
            isChange = 1

            segments = dict(
                flightNumber=flightNumber,
                aircraftType=aircraftType,
                number=1,
                departureTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(depTime)),
                destinationTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(arrTime)),
                airline=carrier,
                dep=depAirport,
                dest=arrAirport,
                seats=maxSeats,
                duration=duration,
                depTerminal=''
            )
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
            # print(item)




    def get_task(self):
        inputFile = open(os.path.join('utils', 'FZ.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 1
        for i in range(8, 30, days):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y-%m-%d')
            for data in datas:
                if not data or not len(data):
                    continue
                yield (data[0], data[1], _dt)

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-' * 40)
        print(failure.value)
        yield failure.request
