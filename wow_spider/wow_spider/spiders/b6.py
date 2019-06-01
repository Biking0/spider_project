# -*- coding: utf-8 -*-
import scrapy,re,time,json,logging,os,csv,random,traceback
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta
from utils import dataUtil
from utils import pubUtil

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



class B6Spider(scrapy.Spider):
    name = 'b6'
    allowed_domains = ['jetblue.com']
    start_urls = ['https://mobile.jetblue.com/h5/r/book.jetblue.com/shop/search/']
    version = 1.4
    task = []
    isOK = False
    data_task = {}
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 200,
            # 'wow_spider.middlewares.XQSessionMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=20,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=3,
        COOKIES_ENABLED=True,
        INVALID_TIME=45,
        #高并发下数据会返回出错的，所以改成1保证数据稳定
        CONCURRENT_REQUESTS=1,
        SEAT=4,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS={
            'ADRUM': 'isAjax',
            'ADRUM_1': 'isMobile',
            'Accept-Encoding': 'gzip',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Host': 'mobile.jetblue.com',
            'Pragma': 'no-cache',
            'User-Agent': 'okhttp/3.8.1',
        },
        CURRENCY_CACHE={
            u'$': u'USD',  # 美元
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
        result_iter = None
        result = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter or not result:
                    result_iter = self.get_task()
                result = next(result_iter)
                print result[0]
            else:
                result = pubUtil.getUrl('B6', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
        #     for i in range(1):
        #     for data in self.get_task():
        #         dep, to, dt = data
                # dt,dep,to= '2018-11-21','RDU','JFK'
                # dt,dep,to= '2018-11-23','BOS','JAX'
                # print(dep, to, dt)
                seat = self.custom_settings.get('SEAT')
                querystring = {
                    'departureAirportCode': dep,
                    'env': 'prod',
                    'jbBookerCurrency-flights': 'usd',
                    'journeySpan': 'OW',
                    'numAdults': seat,
                    'numChildren': '0',
                    'numInfants': '0',
                    'returnAirportCode': to,
                    'startDate': re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\3-\2-\1', dt),
                    'submitted-form': 'bkSearch',
                    'un_jtt_application_platform': 'android',
                    'version': 'ANDROID-v4.6.4'
                }
                url = self.start_urls[0] + '?'
                for key in querystring:
                    url = url + key + '=' + str(querystring.get(key)) + '&'

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
                                     headers=self.custom_settings.get('HEADERS'),
                                     meta={'meta_data': meta_data},
                                     errback=self.errback
                                     )


    def parse(self, response):
        # print(response.text)
        self.isOK = True
        results = response.xpath("//div[@class='results-list']/div[@*]")
        # print(results)
        #分析每个航班
        for result in results:
            #判断中转
            fare_amenities = result.xpath('.//div[@class="fare-amenities"]')
            if len(fare_amenities) > 1:
                # print('is change')
                continue
            #航司网页没显示，设置默认
            carrier ="B6"
            # print(fare_amenities.extract())
            flight_number = str(fare_amenities.xpath('normalize-space(./ul/li[1]//text()[3])').extract()[0])
            # 去掉航班号的**
            flight_number = re.compile("\d+").search(flight_number)
            if not flight_number:
                invalid = response.meta.get('meta_data').get('invalid')
                self.task.append(invalid)
                print("no flight")
                continue

            flightNumber = carrier + flight_number.group()
            data_summary = result.xpath('./div[1]/ul/li')
            dep_time_airport = data_summary[0].xpath('./span/text()').extract()
            depAirport = dep_time_airport[1]
            dt = response.meta.get('meta_data').get('flight_time')
            dep_dt = dt + 'T' + dep_time_airport[0]
            dep_tupletime = time.strptime(dep_dt, '%Y-%m-%dT%I:%M %p')
            depTime = time.mktime(dep_tupletime)

            arr_time_airport = data_summary[2].xpath('./span/text()').extract()
            arrAirport = arr_time_airport[1]
            if arr_time_airport[0][-2:] == "+1":

                # print arr_time_airport[0],response.meta.get('meta_data').get('aaa')
                arr_dt =  pubUtil.time_add_num(dt, 1) + 'T' + arr_time_airport[0][:-2]
            else:
                arr_dt = dt + 'T' + arr_time_airport[0]
            arr_tupletime = time.strptime(arr_dt, '%Y-%m-%dT%I:%M %p')
            arrTime = time.mktime(arr_tupletime)
            price = data_summary[4].xpath('./span[2]/text()').extract()
            if not price:
                currency = "RPG"
                adultPrice = 0
                maxSeats = 0
            else:
                currency = self.custom_settings.get('CURRENCY_CACHE').get(price[0][0],price[0][0])
                adultPrice = float(price[0][1:])
                maxSeats = self.custom_settings.get('SEAT')
            adultTax = 0
            netFare = adultPrice-adultTax
            cabin = 'X'
            isChange = 1
            getTime = time.time()

            #增加套餐价
            price_dict = {
                'Blue': 0,
                'Blue Plus': 0,
                'Blue Flex': 0,
            }
            # aaa = result.xpath('.//div[@class="fare-row BN"]//div[@style="font-size: 18px; margin-top: 3px;"]/text()').extract()
            # print(aaa)
            plus_price = result.xpath('normalize-space(.//div[@class="fare-row CN ribbon"]//div[@style="font-size: 18px; margin-top: 3px;"]/text())').extract()[0][1:]
            if plus_price.replace('.','').isnumeric():
                price_dict['Blue Plus'] = float(plus_price)
            flex_price = result.xpath('normalize-space(.//div[@class="fare-row BN "]//div[@style="font-size: 18px; margin-top: 3px;"]/text())').extract()[0][1:]
            if flex_price.replace('.','').isnumeric():
                price_dict['Blue Flex'] = float(flex_price)
            segments = [[price_dict.get('Blue Plus'),maxSeats],[price_dict.get('Blue Flex'),maxSeats]]
            # print(segments)

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
            # flight_number_time = str(time.strftime('%Y-%m-%dT%H:%M',dep_tupletime)) + flightNumber
            # if not self.data_task.get(flight_number_time):
            #     self.data_task[flight_number_time] = adultPrice
            #     print self.data_task
            yield item
            # print(item,dep_dt,arr_dt,'132312',time.strftime( '%Y-%m-%dT%H:%M',dep_tupletime),time.strftime( '%Y-%m-%dT%H:%M',arr_tupletime))
            # if flightNumber == 'B6894':
            # if (adultPrice,time.strftime( '%Y-%m-%dT%H:%M',dep_tupletime),time.strftime( '%Y-%m-%dT%H:%M',arr_tupletime)) != (276.0, '2018-11-06T19:09', '2018-11-06T22:00'):
            #     print(adultPrice,time.strftime( '%Y-%m-%dT%H:%M',dep_tupletime),time.strftime( '%Y-%m-%dT%H:%M',arr_tupletime))









    def get_task(self):
        print "local task"
        inputFile = open(os.path.join('utils', 'B6.csv'), 'rU')
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
        for i in range(1, 10, days):
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

