# -*- coding: utf-8 -*-
import scrapy, re, time, json, logging, os, csv, random, traceback
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta
from utils import dataUtil
from utils import pubUtil
from jsonpath import jsonpath

"""
              ┏┓      ┏┓
            ┏┛┻━━━┛┻┓
            ┃      ☃      ┃
            ┃  ┳┛  ┗┳  ┃
            ┃      ┻      ┃
            ┗━┓      ┏━┛
                ┃      ┗━━━┓
                ┃  神兽保佑    ┣┓
                ┃　永无BUG！   ┏┛
                ┗┓┓┏━┳┓┏┛
                  ┃┫┫  ┃┫┫
                  ┗┻┛  ┗┻┛
"""


class A4oSpider(scrapy.Spider):
    name = '4o'
    allowed_domains = ['interjet.com.mx']
    start_urls = ['https://aplicaciones.interjet.com.mx/AppsServices/RestServices.svc/availability']
    version = 2.0
    task = []
    isOK = False
    isToken = False
    data_task = {}
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 200,
            'wow_spider.middlewares.A4OTokenMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=20,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=8,
        # COOKIES_ENABLED=True,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=4,
        SEAT=3,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        USER_AGENT=[
            'Dalvik/2.1.0 (Linux; U; Android 8.0.0; SM-G950F Build/R16NW)',
            'Dalvik/2.1.0 (Linux; U; Android 8.0.0; SM-N950U Build/R16NW)',
            'Dalvik/2.1.0 (Linux; U; Android 8.0.0; moto e5 cruise Build/OCPS27.91-32-5)',
            'Dalvik/2.1.0 (Linux; U; Android 7.1.1; SM-N950U Build/NMF26X)',
            'Dalvik/2.1.0 (Linux; U; Android 7.0; LG-TP260 Build/NRD90U)',
            'Dalvik/2.1.0 (Linux; U; Android 7.0; 5049Z Build/NRD90M)',
            'Dalvik/2.1.0 (Linux; U; Android 5.1; A1601 Build/LMY47I)',
            'Dalvik/2.1.0 (Linux; U; Android 5.1.1; VS820 Build/LMY47V)',
            'Dalvik/2.1.0 (Linux; U; Android 5.1.1; LGL51AL Build/LMY47V)',
        ],
        DEFAULT_REQUEST_HEADERS={},
        HEADERS={
            'User-Agent':'Mozilla/5.0 (iPad; CPU OS 10_2 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) CriOS/58.0.3029.113 Mobile/14C92 Safari/602.1',
            # 'Host':'aplicaciones.interjet.com.mx',
            'Accept-Encoding':'gzip',
            # 'Pragma':'no-cache',
            # 'Cache-Control':'no-cache',
            'Connection':'keep-alive',
        },
        TOKEN_URL = "https://aplicaciones.interjet.com.mx/AppsServices/RestServices.svc/login?Password=Interjet-2016&Username=webapi@mobile.com&CultureCode=en-US",
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()
        self.ua_data = self.get_ua()

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
                print result[0]
            else:
                result = pubUtil.getUrl('4O', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
            # for i in range(1):
            # for data in self.get_task():
            #     dep, to, dt = data
                # dt,dep,to= '2018-11-21','MEX','MTY'
                # print(dep, to, dt)
                seat = self.custom_settings.get('SEAT')
                querystring = {
                    'ArrivalStation': to,
                    'CurrencyCode': 'USD',
                    'DepartureDate': dt,
                    'DepartureStation': dep,
                    'PaxResidentCountry': 'US',
                    'ReturnDate': '',
                    'RoleCode': 'WWWA',
                    # 'Signature': '7g45Wa4GSDU%3D%7CFGktbwO8EpThKsp1cB6fKOAqUvn3guMXZi8UTGptOepMgEP4vfdsuDVx9CUEK6PPNKDct2Otx5ujxMUtBdbGAKypdlrDs58IJ5egu0MpkyBUcJAzA3CC5OLpbNF%2B2XmVvSljYUJspk0%3D',
                    # 'Signature': 'D0QxiSJmAVA%3D%7Cu8aeufqyaeaQ8rZDzn%2FfgXgUix%2Fw6vE1NV1boWcJkMxA%2FST6xYdjipCYmvebA4zP%2BVfgbgxJPChcxCy2jn8ur4hAPBprYZ%2F7PBBZr3%2FaXo6aZ018F3GSPm3jNzQzeC3UBXtJs77215s%3D'
                    'TotalPaxAdt': seat,
                    'TotalPaxChd': '0',
                    'TotalPaxInf': '0',
                    'TotalPaxSrc': '0',
                    'Version': '7'
                }
                url = self.start_urls[0] + '?'
                for key in querystring:
                    url = url + key + '=' + str(querystring.get(key)) + '&'
                headers = self.custom_settings.get('HEADERS')
                # headers['User-Agent'] = random.choice(self.ua_data)[0]
                headers['User-Agent'] = self.ua_construction()
                # print '请求：', headers['User-Agent']
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME'),
                }
                meta_data = dict(
                    invalid=invalid,
                    params=querystring,
                    aaa=(dep, to, dt),
                    flight_time=dt,
                    url=url,
                )
                yield scrapy.Request(url,
                                     callback=self.parse,
                                     method='GET',
                                     headers=headers,
                                     meta={'meta_data': meta_data},
                                     errback=self.errback
                                     )



    def parse(self, response):
        # print response.text
        self.isOK = True
        data = json.loads(response.text)
        self.isToken =True
        response_code = data.get('ResponseCode')
        if response_code in ["-1","100"]:
            # 无效机场
            if data.get('Message') != "Session Token authentication failure.":
                print "invalid station:%s"%data.get('Message')
                return
            self.isToken = False
            yield scrapy.Request(response.meta.get("meta_data").get('url'),
                                 callback=self.parse,
                                 method='GET',
                                 headers=self.custom_settings.get('HEADERS'),
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback
                                     )
            return
        # 没有数据错误，换代理
        if response_code in ["12"]:
            self.isOK = False
            print "proxy invalid"
            yield scrapy.Request(response.meta.get("meta_data").get('url'),
                                 callback=self.parse,
                                 method='GET',
                                 headers=self.custom_settings.get('HEADERS'),
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback
                                     )
            return
        schedules = data.get('SchedulesIj')
        #判断没有航班时
        if not schedules:
            print("not flight today")
            # print response.text
            invalid = response.meta.get("meta_data").get("invalid")
            self.task.append(invalid)
            return
        journeys = schedules[0].get('JourneysIj')
        for journey in journeys:
            #判断中转
            flight_segments = journey.get('SegmentsIj')
            if len(flight_segments) > 1:
                # print "is change"
                continue
            #把需要的数据从JourneySellKey取出来
            sell_data = re.split(r'~[~|\s]*', journey.get('JourneySellKey'))
            carrier = sell_data[0]
            flightNumber = carrier + sell_data[1]
            depAirport = sell_data[2]
            arrAirport = sell_data[4]
            deptime_tuple = time.strptime(sell_data[3], '%m/%d/%Y %H:%M')
            depTime = time.mktime(deptime_tuple)
            arrtime_tuple = time.strptime(sell_data[5], '%m/%d/%Y %H:%M')
            arrTime = time.mktime(arrtime_tuple)

            fares = flight_segments[0].get('FaresIj')
            adultPrice,adultTax,maxSeats,currency,cabin = 0,0,0,"",'X'
            #有票价时判断
            if fares:
                adultPrice = fares[0].get('TotalFare')
                currency = jsonpath(fares[0],'$..CurrencyCode')[0]
                maxSeats = self.custom_settings.get('SEAT')
                cabin = fares[0].get('ClassOfService')
            netFare = adultPrice - adultTax
            isChange = 1
            getTime = time.time()

            # 增加套餐价格,先定义价格表
            price_dict = {
                'ECO': 0,
                'ADVANTAGE': 0,
                'EXTRA': 0,
                'SUPER_ECO': 0
            }


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






    def get_ua(self):
        ua_data = open(os.path.join('utils','4O_UA.csv'),'rU')
        ua_reader = csv.reader(ua_data)
        datas = list(ua_reader)
        ua_data.close()
        return datas


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

    def get_task(self):
        print "local task"
        inputFile = open(os.path.join('utils', '4O.csv'), 'rU')
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
            _dt = _date.strftime('%Y%m%d')
            for data in datas:
                if not data or not len(data):
                    continue
                # yield (data[0], data[1], _dt)
                yield ['%s-%s:%s:1' % (data[0], data[1], _dt)]
                # task = [('VKO','BGY','2018-10-06'),('BGY','LED','2018-10-06'),('VKO','PSA','2018-10-06')]
                # for i in task:
                #     yield i

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-' * 40)
        print(failure.value)
        yield failure.request

