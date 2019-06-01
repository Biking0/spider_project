# -*- coding: utf-8 -*-
import scrapy,json,time,csv,os,random,logging
from utils import dataUtil
from utils import pubUtil
from datetime import datetime, timedelta
from wow_spider.items import WowSpiderItem


class A5jSpider(scrapy.Spider):
    name = '5j'
    allowed_domains = ['azure-api.net']
    start_urls = ['https://mobile-api.cebupacificair.com/dotrez-prod-v2/api/nsk/v1/availability/lowfare']
    version = 1.9
    task = []
    isOK = False
    custom_settings = dict(
        CONCURRENT_REQUESTS=2,
        SEAT=3,
        DURATION=7,
        DOWNLOAD_TIMEOUT=30,
        IP_URL='http://lumtest.com/myip.json',
        IP_PROXY='http://lum-customer-henanzhenxiang-zone-zhuzhai-session-%s-country-hk:7zgxeegnwaeo@zproxy.lum-superproxy.io:22225',
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            # 'wow_spider.middlewares.MMProxyMiddleware': 200,
            'wow_spider.middlewares.a5JtokenMiddleware': 300,

        },
        CLOSESPIDER_TIMEOUT=0,
        # ITEM_PIPELINES = {
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS={
            'ocp-apim-subscription-key': "07ce68d9937841a59a8156ec7dafc0b6",
            # 'loggly-tracking-id': "719761",
            # 'authorization-secret': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBuYW1lIjoiY2VidXBhY2lmaWMiLCJ2ZXJzaW9uIjoiMi4xNy4wIiwicGxhdGZvcm0iOiJBTkRST0lEIiwibG9nZ2x5SWQiOiIxNjc5NzkifQ.On2cf_95J-DzuaqBeLSm5U4knAzL306Znd_I-hKqfiQ",
            # 'Authorization-Secret': "",
            'Authorization-Secret': "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBuYW1lIjoiY2VidXBhY2lmaWMiLCJ2ZXJzaW9uIjoiMi4yMi4wIiwicGxhdGZvcm0iOiJBTkRST0lEIiwibG9nZ2x5SWQiOiI5NTI3NTUifQ.L13atRF3BXukVo7OuUbh2r8JwV3Ca6jZETSmTwTTzEw",
            # 'authorization': '',
            # 'authorization':'',
            'accept': "application/json",
            'content-type': "application/json; charset=utf-8",
            # 'host': "cebmobileapi.azure-api.net",
            'accept-encoding': "gzip",
            'user-agent': "okhttp/2.3.0",
            'connection': "keep-alive",

        },
        TOKEN_URL="https://mobile-api.cebupacificair.com/dotrez-prod-v2/api/v1/Token",
        ADMIN_FEES={},

        # SEGMENTS_FEES={},

    )


    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()
        self.custom_settings['ADMIN_FEES'] = pubUtil.get_tax()
        # self.custom_settings['SEGMENTS_FEES'] = pubUtil.get_segments()
        # print(self.custom_settings.get('ADMIN_FEES'))


    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name,self.name,self.num,permins,self.version))
        result_iter = None
        result = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter or not result:
                    result_iter = self.get_task()
                result = next(result_iter)
            else:
                result = pubUtil.getUrl('DG', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to,days) = pubUtil.analysisData_5j(data)
            # for data in self.get_task():
            #     dep, to, dt, days = data
                print(dep, to, dt)
                # dt,dep,to,days = '2018-09-04','MNL','PEK',7
                seat = self.custom_settings.get('SEAT')

                duration = self.custom_settings.get("DURATION")
                # self.log('%s:%s:%s:%s' % (dt, dep, to, days), 20)
                for i in range(0,int(days),duration):
                    begin_dt,end_dt =pubUtil.time_add_5j(dt,i, duration)
                     # = pubUtil.time_add_5j(dt,i)
                    # print(dep,to,begin_dt,end_dt)
                    payload = {
                        "IncludeTaxesAndFees": True,
                        "Passengers": {
                            "Types": [{
                                "Type": "ADT",
                                "Count": seat
                            }]
                        },
                        "Codes": {
                            "Currency": ""
                        },
                        "Filters": {
                            "BookingClasses": ["Y", "U", "S", "B", "H", "M", "K", "L", "Q", "G", "W", "V", "C", "D", "E",
                                               "Z", "PA", "PD", "A", "P", "FC", "FD", "FE", "T", "O", "TA", "TC", "TD",
                                               "TJ", "OM"],
                            "ProductClasses": []
                        },
                        "Criteria": [{
                            "DestinationStationCodes": [to],
                            "OriginStationCodes": [dep],
                            "BeginDate": "%sT00:00:00"%begin_dt,
                            "EndDate": "%sT00:00:00"%end_dt
                        }]
                    }

                    invalid = {
                        'date': begin_dt.replace('-', ''),
                        'depAirport': dep,
                        'arrAirport': to,
                        'mins': self.custom_settings.get('INVALID_TIME')
                    }
                    body=json.dumps(payload)
                    meta_data = dict(
                        invalid=invalid,
                        payload=body,
                        begin_dt=begin_dt,
                        add_day = i,
                        duration = duration
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
        self.isOK = True
        try:
            data = json.loads(response.body)
        except:
            self.isOK=False
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=response.meta.get('meta_data').get('payload'),
                                 callback=self.parse,
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback)
            return


        if data.get('errors'):
            self.isOK = False
            if data.get('errors')[0].get('message') == 'nsk-server:InvalidStationCode' or 'nsk-server:AuthorizationStationCategoryNotAllowed':
                print('Invalid airfield pair')
                return
            print('get data error')
            # print(data.get('errors'))
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=response.meta.get('meta_data').get('payload'),
                                 callback=self.parse,
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback)
            return

        if data.get('message') or data.get('statusCode'):
            # print('6' * 66)
            print(data.get('message'))
            # time.sleep(20)
            self.isOK = False
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=response.meta.get('meta_data').get('payload'),
                                 callback=self.parse,
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback)
            return

        currency= data.get('data').get('currencyCode')
        if not currency:
            num_day = 0
            for lowFareDateMarket in data.get('data').get('lowFareDateMarkets'):
                lowFares = lowFareDateMarket.get('lowFares')
                if len(lowFares) == 0:
                    num_day += 1
                else:
                    break
            meta = response.meta.get('meta_data')
            payload = meta.get('payload')
            begin_dt=meta.get('begin_dt')
            add_day=meta.get('add_day')+ num_day
            duration = meta.get('duration')-num_day
            invalid = meta.get('invalid')
            date = invalid.get('date')
            new_date = datetime.strptime(date, '%Y%m%d')
            for i in range(num_day):
                date_time = new_date + timedelta(days=i)
                # print(date_time)
                invalid['date'] = date_time.strftime('%Y%m%d')
                self.task.append(invalid)
            if duration <= 0:
                print('No flight on current date')
                return
            begin_dt, end_dt = pubUtil.time_add_5j(begin_dt, add_day, duration)
            payload = json.loads(payload)
            payload['Criteria'][0]['BeginDate'] = "%sT00:00:00" % begin_dt
            payload['Criteria'][0]['EndDate'] = "%sT00:00:00" % end_dt
            payload = json.dumps(payload)
            invalid = meta.get('invalid')
            invalid['date'] = begin_dt.replace('-', '')
            meta_data = dict(
                invalid=invalid,
                payload=payload,
                begin_dt=begin_dt,
                add_day=meta.get('add_day'),
                duration = duration
            )
            print('No flight today,to requests new time:%s,%s'% (begin_dt, end_dt))
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=payload,
                                 callback=self.parse,
                                 meta={'meta_data': meta_data},
                                 errback=self.errback)
            return
        lowFareDateMarkets=data.get('data').get('lowFareDateMarkets')
        #显示几天结果的列表
        for lowFareDateMarket in lowFareDateMarkets:
            #取出当天航班列表
            lowFares = lowFareDateMarket.get('lowFares')
            for lowFare in lowFares:
                #先进行判断是否中转
                legs = lowFare.get('legs')
                if len(legs) > 1:
                    continue

                leg=legs[0]
                carrier =leg.get('carrierCode')
                flightNumber='%s%s'%(carrier,leg.get('flightNumber'))
                deptime = time.strptime(leg.get('departureTime'), '%Y-%m-%dT%H:%M:%S')
                depTime = time.mktime(deptime)
                arrtime = time.strptime(leg.get('arrivalTime'), '%Y-%m-%dT%H:%M:%S')
                arrTime = time.mktime(arrtime)
                depAirport = leg.get('origin')
                arrAirport = leg.get('destination')
                aircraftType = leg.get('equipmentType')

                admin_tax = self.custom_settings.get('ADMIN_FEES').get('%s%s'%(depAirport,arrAirport))
                if not admin_tax.get('currency') == currency or not admin_tax:
                    invalid = response.meta.get('meta_data').get('invalid')
                    invalid['date'] = time.strftime('%Y%m%d',deptime)
                    # print('--------------------------------------------invaild:%s----------------------------------------'%time.strftime('%Y%m%d',deptime))
                    self.task.append(invalid)
                    continue
                # adultPrice = netFare + adultTax + float(self.custom_settings.get('ADMIN_FEES').get('%s%s'%(depAirport,arrAirport)))
                fares = lowFare.get('passengers').get('ADT')
                netFare = fares.get('fareAmount')
                adultTax = fares.get('taxesAndFeesAmount') + float(admin_tax.get('tax'))
                adultPrice = netFare + adultTax
                maxSeats = lowFare.get('availableCount')
                cabin = lowFare.get('bookingClasses')[0]
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
                    duration=dataUtil.gen_duration(depTime, arrTime),
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
        print "local task"
        inputFile = open(os.path.join('utils', '5J.csv'),'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 7
        for i in range(1, 30, days):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y%m%d')
            for data in datas:
                if not data or not len(data):
                    continue
                # yield (data[0], data[1], _dt, days)
                yield ['%s-%s:%s:%s' % (data[0], data[1], _dt, days)]



    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-'*40)
        print(failure.value)
        yield failure.request
