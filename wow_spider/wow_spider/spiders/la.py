# -*- coding: utf-8 -*-
import scrapy,re,time,json,logging,os,csv,random,traceback
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta
from utils import dataUtil
from utils import pubUtil



class LaSpider(scrapy.Spider):
    name = 'la'
    allowed_domains = ['latam.com']
    start_urls = ['https://bff.latam.com/ws/proxy/booking-webapp-bff/v1/public/revenue/recommendations/oneway']
    version = 1.1
    task = []
    isOK = True
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            # 'wow_spider.middlewares.ProxyMiddleware': 200,
            # 'wow_spider.middlewares.XQSessionMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=20,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=8,
        # COOKIES_ENABLED=True,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=8,
        SEAT=5,
        ITEM_PIPELINES={
            'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        },
        HEADERS={
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            'accept': "application/json, text/plain, */*",
            'referer': "https://www.latam.com/pt_br/apps/personas/booking",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
        },
        CURRENCY_CACHE={
            u'$': u'USD',  # 美元
            u'руб.': u'RUB',  # 卢布
            # u'THB': u'THB',
            # u'HK$': u'HKD',  # 港币
            # u'NT$': u'TWD',  # 台币
            # u'CNY': u'CNY',
        },
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl('LA', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
            # for i in range(1):
            # for data in self.get_task():
            #     dep, to, dt = data
                # dt,dep,to= '2018-10-16','CWB','SAO'
                # print(dep, to, dt)
                currency = "BR"
                seat = self.custom_settings.get('SEAT')
                querystring = {
                    "country": currency,
                    "origin": dep,
                    "destination": to,
                    "departure": dt,
                    "adult": seat,
                }
                url = self.start_urls[0] + '?'
                for key in querystring:
                    url = url + key + '=' + str(querystring.get(key)) + '&'

                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                meta_data = dict(
                    invalid=invalid,
                    params=querystring,
                    aaa=(dep, to, dt),
                    flight_time=dt
                )
                yield scrapy.Request(url,
                                     callback=self.parse,
                                     method='GET',
                                     headers=self.custom_settings.get('HEADERS'),
                                     meta={'meta_data': meta_data},
                                     errback=self.errback
                                     )


    def parse(self, response):
        # print(response.text)
        data = json.loads(response.text).get('data')
        # flights = data.get('flights')
        try:
            currency = data.get('currency')
        except:
            print response.text
            traceback.print_exc()
            return
        for flight in data.get('flights'):
            #当天没有航班设定失效
            if not flight:
                invalid = response.meta.get('invalid')
                self.task.append(invalid)
                # print("no flight")
                continue
            #先判断中转
            flight_segments = flight.get('segments')
            if len(flight_segments) > 1:
                continue
            flight_segment = flight_segments[0]
            carrier = flight_segment.get('airline').get('code')
            flightNumber = flight_segment.get('flightCode')
            departure = flight_segment.get('departure')
            deptime_tuple = time.strptime(departure.get('dateTime')[:-6], '%Y-%m-%dT%H:%M')
            depTime = time.mktime(deptime_tuple)
            arrival = flight_segment.get('arrival')
            arrtime_tuple = time.strptime(arrival.get('dateTime')[:-6], '%Y-%m-%dT%H:%M')
            arrTime = time.mktime(arrtime_tuple)
            depAirport = departure.get('airportCode')
            arrAirport = arrival.get('airportCode')

            #选取最低票价,在列表里面，暂时先不做
            fares = flight.get('cabins')[0].get('fares')
            cabin = fares[0].get('code')
            fare = fares[0].get('price').get('adult')
            adultPrice = fare.get('total')
            adultTax = fare.get('taxAndFees')
            netFare = fare.get('amountWithoutTax')


            isChange = 1
            getTime = time.time()
            maxSeats = self.custom_settings.get('SEAT')

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
            item['segments'] = '123:123:1223'
            item['getTime'] = getTime
            yield item
            # print(item)









    def get_task(self):
        inputFile = open(os.path.join('utils', 'LA.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
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
                # task = [('VKO','BGY','2018-10-06'),('BGY','LED','2018-10-06'),('VKO','PSA','2018-10-06')]
                # for i in task:
                #     yield i

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-' * 40)
        print(failure.value)
        yield failure.request

