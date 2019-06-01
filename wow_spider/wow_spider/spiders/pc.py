# -*- coding: utf-8 -*-
import scrapy,json,time,csv,os,random,logging,traceback
from utils import dataUtil
from utils import pubUtil
from datetime import datetime, timedelta
from wow_spider.items import WowSpiderItem


class PcSpider(scrapy.Spider):
    name = 'pc'
    allowed_domains = ['flypgs.com']
    start_urls = ['https://mw.flypgs.com/pegasus/availability']
    version = 1.9
    task = []
    isOK = False
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.IPV4ProxyMiddleware': 200,
            # 'wow_spider.middlewares.MMcookieMiddleware': 300,

        },
        CONCURRENT_REQUESTS=12,
        # ITEM_PIPELINES = {
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS={
            'accept-language': "en",
            'x-platform': "android",
            'x-version': "2.4.0",
            'x-system-version': "4.4.2",
            'x-device-id': "9a541b5e362a3356",
            'content-type': "application/json; charset=UTF-8",
            'host': "mw.flypgs.com",
            'accept-encoding': "gzip",
            'user-agent': "okhttp/3.9.0",
            'connection': "keep-alive",
        },
        SEAT=3,
        CURRENCY_CACHE={
            u'TL': u'TRY',
        },


    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

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
                result = pubUtil.getUrl('PC', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                print data
                (dt, dep, to) = pubUtil.analysisData(data)
                # dt,dep,to = '2018-08-30','TZX','SAW'
                seat = self.custom_settings.get('SEAT')
                payload = {
                    "flightSearchList": [{
                        "arrivalPort": to,
                        "departurePort": dep,
                        "departureDate": dt
                    }],
                    "adultCount": seat,
                    "childCount": 0,
                    "infantCount": 0,
                    "soldierCount": 0,
                    "currency": "TL",
                    "operationCode": "TK",
                    "ffRedemption": False,
                    "openFlightSearch": False,
                    "personnelFlightSearch": False,
                    "dateOption": 1
                }
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                yield scrapy.Request(self.start_urls[0],
                                     callback=self.parse,
                                     method='POST',
                                     headers=self.custom_settings.get('HEADERS'),
                                     meta={'invalid': invalid},
                                     body=json.dumps(payload),
                                     errback=self.errback)


    def parse(self, response):
        self.isOK = True
        # print('*'*50)
        json_dict = json.loads(response.body)
        try:
            daily_flight_list = json_dict.get('departureRouteList')[0].get('dailyFlightList')
        except:
            return
        #这个请求会显示三天的航班，在这个列表里
        for daily_flight in daily_flight_list:
            #分析当天航班列表
            flightList = daily_flight.get('flightList')
            if not flightList:
                invalid = response.meta.get('invalid')
                invalid['date'] = daily_flight.get('date').replace('-', '')
                self.task.append(invalid)
                # print("no flight")
                continue
            for flight in flightList:
                #判断是否是中转
                if flight.get('connectedFlight'):
                    # print('is change')
                    continue

                fare_seat = flight.get('fare')
                #判断是否有票
                if not fare_seat:
                    #没票是设置为0
                    maxSeats =0
                    adultPrice = 0
                    currency = 'TRY'
                    cabin = 'X'
                    net_fare = 0
                else:
                    #目前发现是座位数少才会显示，先这样做判断，以后数量多在分析
                    if fare_seat.get('remainingSeatLabel'):
                        maxSeats = int(fare_seat.get('remainingSeatLabel').get('values')[0])
                    else:
                        maxSeats = 9
                    adultPrice = fare_seat.get('shownFare').get('amount')
                    currency_symbol = fare_seat.get('shownFare').get('currency')
                    currency = self.custom_settings.get('CURRENCY_CACHE').get(currency_symbol) or currency_symbol
                    cabin = fare_seat.get('reservationClass')
                    net_fare = fare_seat.get('totalFareDetailList')[0].get('subDetailList')[0].get('amount').get('amount')
                netFare = net_fare / self.custom_settings.get('SEAT')
                adultTax = adultPrice - netFare
                isChange = 1
                carrier = flight.get('airline')
                flightNumber = '%s%s' % (carrier, flight.get('flightNo'))
                deptime = time.strptime(flight.get('departureDateTime'), '%Y-%m-%dT%H:%M:%S')
                depTime = time.mktime(deptime)
                arrtime = time.strptime(flight.get('arrivalDateTime'), '%Y-%m-%dT%H:%M:%S')
                arrTime = time.mktime(arrtime)
                dep_city_port_name = flight.get('departureLocation')
                arr_city_port_name = flight.get('arrivalLocation')
                # fromCity = dep_city_port_name.get('cityCode')
                # toCity = arr_city_port_name.get('cityCode')
                depAirport = dep_city_port_name.get('portCode')
                arrAirport = arr_city_port_name.get('portCode')

                #增加套餐价格,先定义价格表
                price_dict = {
                    'ECO' : 0,
                    'ADVANTAGE' : 0,
                    'EXTRA' : 0,
                    'SUPER_ECO' : 0
                }
                if adultPrice !=0:
                    bundleList = fare_seat.get('bundleList')
                    for bundle in bundleList:
                        package_name = bundle.get('bundleType')
                        package_price = bundle.get('shownFare').get('amount')
                        price_dict[package_name] = package_price


                # segments = '%s:%s:%s' % (price_dict.get('ECO'), price_dict.get('ADVANTAGE'), price_dict.get('EXTRA'))
                segments = [[price_dict.get('ECO'),maxSeats],[price_dict.get('ADVANTAGE'),maxSeats],[price_dict.get('EXTRA'),maxSeats]]
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
        inputFile = open(os.path.join('utils', 'PC.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now()
        # #倒序输出
        # datas = datas[::-1]
        #打乱顺序
        random.shuffle(datas)
        for i in range(1,15,3):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y%m%d')
            for data in datas:
                if not data or not len(data):
                    continue
                # yield (data[0], data[1], _dt)
                yield ['%s-%s:%s:1' % (data[0], data[1], _dt)]
