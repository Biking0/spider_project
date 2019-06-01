# -*- coding: utf-8 -*-
import scrapy, json, time, csv, os, random, logging, traceback, sys, re
from utils import dataUtil
from utils import pubUtil
from utils import log_mail
from datetime import datetime, timedelta
from wow_spider.items import WowSpiderItem


class TrSpider(scrapy.Spider):
    name = 'tr'
    allowed_domains = ['wxflyscoot.com']
    start_urls = ['https://www.wxflyscoot.com/home/booking/ajax_search']
    version = 1.3
    task = []
    isOK = True
    custom_settings = dict(
        CONCURRENT_REQUESTS=1,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            # 'wow_spider.middlewares.ProxyMiddleware': 200,
            'wow_spider.middlewares.TRMiddleware': 300,
        },
        DEFAULT_REQUEST_HEADERS={},
        HEADERS={
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-cn',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            # 'Cookie': 'kuhang_=99rrjlcn1appuopice544rkf7l1er5gq;',
            'Cookie': 'kuhang_=fiths505s7tjel11eaafpp1dqmupfqer;',
            # 'Cookie': 'Hm_lpvt_36a21581fba651026d79607ab17269c7=1547105745; Hm_lvt_36a21581fba651026d79607ab17269c7=1547105630',
            'Host': 'www.wxflyscoot.com',
            'Origin': 'https://www.wxflyscoot.com',
            'Referer': 'https://www.wxflyscoot.com/home/booking/index',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/7.0.1(0x17000120) NetType/WIFI Language/zh_CN',
            'X-Requested-With': 'XMLHttpRequest'
        },
        SEAT=1,
        COOKIE_LIST=[
            '462g1mp0lrpe0ei0rk4u4a3ugu8tmnjk',
            'fiths505s7tjel11eaafpp1dqmupfqer',
            'lq1464e3su311bd09snot4u5borqpq94',
            '2vp2mvnbuuoq7gbt4ifoi0ikv47ocp72',
            'c8omkqhbvj9h2jmq367k9olvic274l9k',
            '2vtujr38uanvsfvq02hbdur4hkn76pjf',
            'lkhkdrv6ucc4092ofduschvqcs96r1sj'
        ]
        # CURRENCY_CACHE={
        #     u'$': u'AUD',
        # },

    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()
        # 全局更换cookie
        cookie = random.choice(self.custom_settings.get('COOKIE_LIST'))
        self.custom_settings.get('HEADERS')['Cookie'] = 'kuhang_=%s;' % cookie
        print '使用cookie：%s进行访问' % cookie

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        result_iter = None
        result = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter or not result:
                    # 本地任务未编写
                    result_iter = self.get_task()
                result = next(result_iter)
            else:
                result = pubUtil.getUrl('TR', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
                # dt, dep, to = '2019-01-12', 'SIN', 'TAO'
                print dt, dep, to
                seat = self.custom_settings.get('SEAT')
                querystring = {
                    'adt': seat,
                    'arcity': to,
                    'chd': '0',
                    'dpcity': dep,
                    'dpdate': dt,
                    'inft': '0',
                    'promo': '',
                    'type': '1'
                }
                data = ''
                for key in querystring:
                    data = data + key + '=' + str(querystring.get(key)) + '&'
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                meta_data = dict(
                    invalid=invalid,
                    data=data,
                )
                yield scrapy.Request(self.start_urls[0],
                                     callback=self.parse,
                                     headers=self.custom_settings.get('HEADERS'),
                                     method='POST',
                                     meta={'meta_data': meta_data},
                                     body=data,
                                     errback=self.errback)

    def parse(self, response):
        # print('*'*50)
        # print response.text
        # 数据存储在meta里，在middleware有解释
        res = response.request.meta.get('response')
        # if res.status_code == 502:
        #     #
        #     return
        try:
            flight_list = re.compile("console.log\(\[(.*?)\]\);").findall(res.text)
        except:
            try:
                log_mail.log_mail('TRcookie：失效'%response.request.headers.get('Cookie'))
            except:
                pass
            # 全局更换cookie
            cookie = random.choice(self.custom_settings.get('COOKIE_LIST'))
            self.custom_settings.get('HEADERS')['Cookie'] = 'kuhang_=%s;' % cookie
            print '之前cookie失效，使用cookie：%s进行访问' % cookie
            meta_data = response.meta.get('meta_data')
            yield scrapy.Request(self.start_urls[0],
                                 callback=self.parse,
                                 headers=self.custom_settings.get('HEADERS'),
                                 method='POST',
                                 meta={'meta_data': meta_data},
                                 body=meta_data.get('data'),
                                 errback=self.errback)
            return

        if len(flight_list) == 0:
            # 当天无航班
            return

        for i in flight_list:
            flight = json.loads('[' + i + ']')

            # 判断中转
            if len(flight) > 1:
                continue
            flight = flight[0]
            arrAirport = flight.get('ArrivalStation')
            depAirport = flight.get('DepartureStation')
            carrier = flight.get('CarrierCode')
            flightNumber = '%s%s' % (carrier, flight.get('FlightNumber').replace(' ', ''))
            deptime = time.strptime(flight.get('STD'), '%Y-%m-%dT%H:%M:%S')
            depTime = time.mktime(deptime)
            arrtime = time.strptime(flight.get('STA'), '%Y-%m-%dT%H:%M:%S')
            arrTime = time.mktime(arrtime)

            isChange = 1
            # 存在多种票价
            fares = flight.get('Fares')
            # 增加套餐价格,先定义价格表
            price_dict = {
                'E1': [0, 0],
                'E2': [0, 0],
                'E3': [0, 0],
                'J': [0, 0],
            }
            adultPrice, adultTax, netFare, cabin, maxSeats, currency = 0, 0, 0, 'X', 0, None
            for key in fares.keys():
                # 获取不同套餐的价格
                adult_Tax, net_Fare = 0, 0
                fare = fares.get(key)
                prices = fare.get('PaxFare').get('ADT').get('BookingServiceCharge')
                for price in prices:
                    # 获取税价和净票价
                    if price.get('ChargeType') == 'FarePrice':
                        net_Fare = price.get('Amount')
                    else:
                        adult_Tax = adult_Tax + price.get('Amount')
                    if currency:
                        if currency != price.get('CurrencyCode'):
                            break
                    else:
                        currency = price.get('CurrencyCode')
                try:
                    adult_Price = net_Fare + adult_Tax
                except:
                    print net_Fare, adult_Tax, json.dumps(prices)
                    traceback.print_exc()
                    print '6'*66, json.dumps(fares), '6'*66,
                    return
                cabin_ = fare.get('FareBasisCode')[0]
                maxSeats = fare.get('AvailableCount')
                price_dict[key] = [adult_Price, maxSeats]
                if key == 'E1':
                    adultPrice, adultTax, netFare,cabin = adult_Price, adult_Tax, net_Fare, cabin_
                # info = {'farekey': fare.get('FareSellKey')}

            segments = [
                [x for x in price_dict.get('E2')],
                [x for x in price_dict.get('E3')],
                # [x for x in price_dict.get('J')],
            ]
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
            # item['info'] = json.dumps(info)
            yield item
            # print(item)

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-' * 40)
        print(failure.value)
        # yield failure.request

    def get_task(self):
        print "local task"
        inputFile = open(os.path.join('utils', 'TR.csv'), 'rU')
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