# -*- coding: utf-8 -*-
import scrapy, requests
# import locale
import re, time, urllib, json, traceback
from datetime import datetime, timedelta
from dateutil import relativedelta

from lamudatech_dev.items import FlightsItem
from utils.process_airport_city.get_airport_city import get_airport_city
from utils import pubUtil
from lamudatech_dev import settings
from lamudatech_dev.pipelines import LamudatechDevPipeline


class EwSpider(scrapy.Spider):
    name = 'ew'
    spider_name = 'ew'
    version = 1.2

    start_urls = 'https://mobile.eurowings.com/booking/Deeplink.aspx?'
    currency_cache = {
        u'€': u'EUR',
        u'$': u'USD',
        u'£': u'GBP',
        }
    is_ok = True
    proxy = None

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Host': 'mobile.eurowings.com',
            'Proxy-Connection': 'keep-alive',
            'systeminfo': 'iOS',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_3_3 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Mobile/13G34',
            'Accept-Language': 'zh-cn',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        },

        DOWNLOADER_MIDDLEWARES={
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.EwProcessCookies': 401,
        },
        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        CONCURRENT_REQUESTS=8,
        CLOSESPIDER_TIMEOUT=60*60*2,
        HTTPERROR_ALLOWED_CODES=[302],
        # DOWNLOAD_DELAY=3,
        # DOWNLOAD_TIMEOUT=6,
        # COOKIES_ENABLED=False,
        # COOKIES_DEBUG=True,
        # LOG_FILE='log/%s-spider.log' % name,
        # LOG_LEVEL='DEBUG',
    )
    # locale.setlocale( locale.LC_ALL, 'en_US.UTF-8' )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter or not result:
                    result_iter = pubUtil.get_task(self.name)
                result = next(result_iter)
            else:
                try:
                    data_api = settings.GET_TASK_URL + 'carrier=EW'
                    result = json.loads(requests.get(data_api, timeout=180).text).get('data')
                except Exception as e:
                    self.log(e)
                    result = None

            if not result:
                self.log('Date is None!', level=20)
                self.log('Waiting...', level=20)
                time.sleep(16)
                continue

            airports, _day, _num = result[0].split(':')
            FROM, TO = airports.split('-')
            # FROM, TO = 'HAM', 'CDG'

            # 请求最低价获得有价格的日期
            for record in self.get_data(FROM, TO):
                # 日期排序
                order_list = [x.get('date') for x in sorted(record, key=lambda x: x.get('date'))]
                # 筛选临近日期,减少爬取数量
                lowfares = [x for x in record if x.get('date') in self.get_list(order_list)]

                for data in lowfares:
                    _from = data.get('origin')
                    _to = data.get('destination')
                    # currency = data.get('currency')
                    # currency = self.currency_cache.get(currency, currency)
                    _date = data.get('date')
                    # _date = '2018-11-06'
                    params = urllib.urlencode(dict(
                        o=_from,
                        d=_to,
                        t='o',
                        od=_date,
                        adt='5',
                        lng='en-GB',
                        appvi='2D53F50C85034ECF-6000119C00002033',
                        adobe_mc='TS=%s|MCAID=2D791936852A6702-40000129C00FCFCA' % int(time.time()),
                        screen='Search',
                        culture='en-GB',
                    ))

                    total_url = self.start_urls + params

                    yield scrapy.Request(total_url,
                                         meta={'FROM':_from, 'TO': _to, '_day': _date,
                                               # 'currency': currency
                                               },
                                         dont_filter=True,
                                         callback=self.parse,
                                         errback=self.download_errback
                                         )

    def download_errback(self, failure):
        self.log(failure.value, level=40)
        self.is_ok = False

    def parse(self, response):
        meta = response.meta
        FROM = meta.get('FROM')
        TO = meta.get('TO')
        _day = meta.get('_day')
        # currency = meta.get('currency')
        a_tags = response.xpath('//*[@id="tripDeparture"]/div[@class="tripJourneys"]/div[contains(@class, "tripJourneyDate")]/div[contains(@class, "tripJourneyDateFlight")]')
        for trip in a_tags:
            a = trip.xpath('a[contains(@class, "list-box")]')
            content = a.xpath('@data-sellkey').extract_first()
            # 跳过中转航班
            if '^' in content:
                continue

            s = filter((lambda x: x), re.split(r'[~|\s]+', content))
            carrier, number, depAirport, date_from, time_from, arrAirport, date_to, time_to = s

            # 无价格标签说明以售完
            price_str = a.xpath('div[@class="flight-wrapper"]//div[contains(@class, "flight-price-wrapper")]/span[contains(@class,"price")]/span[@class="value"]/text()').extract_first()
            if price_str:
                currency, price = re.match(r'(\D.*?)(\d.*)', price_str).groups()
                # price = locale.atof(price)
                price = float(re.sub(r',', '', price))
                currency = currency.strip()
                currency = self.currency_cache.get(currency, currency)
                maxSeats = 5
                price_dif = [[0, 0]] * 2
                keys = ['SMART', 'BIZclass']
                trip_list = trip.xpath('div[@class="tariffList"]/div[contains(@class, "tripFare") and not(contains(@class, "sold-out"))]')
                price_flag = price
                for trip_i in trip_list:
                    key = trip_i.xpath('./@data-tariff').extract()[0]
                    if key not in keys:
                        continue
                    price_i = trip_i.xpath('./@data-price').extract()[0]
                    price_i = float(re.findall(r'.*?(\d.*)', price_i)[0].replace(',', '')) # 获取此服务的价格
                    if price_i < price_flag:
                        price_i = price_flag
                    else:
                        price_flag = price_i
                    price_dif[keys.index(key)] = [price_i, maxSeats]
            else:
                currency = ''
                price = 0
                maxSeats = 0
                price_dif = None

            fromCity = self.city_airport.get(depAirport, depAirport)
            toCity = self.city_airport.get(arrAirport, arrAirport)

            item = FlightsItem()
            item.update(dict(
                flightNumber=carrier+number,  # 航班号
                depTime=time.mktime(time.strptime(date_from+time_from, "%m/%d/%Y%H:%M")).__int__(),  # 出发时间
                arrTime=time.mktime(time.strptime(date_to+time_to, "%m/%d/%Y%H:%M")).__int__(),  # 达到时间
                fromCity=fromCity,  # 出发城市
                toCity=toCity,  # 到达城市
                depAirport=depAirport,  # 出发机场
                arrAirport=arrAirport,  # 到达机场
                currency=currency,  # 货币种类
                adultPrice=price,  # 成人票价
                adultTax=0,  # 税价
                netFare=price,  # 净票价
                maxSeats=maxSeats,  # 可预定座位数
                cabin='BASIC',  # 舱位
                carrier=carrier,  # 航空公司
                isChange=1,  # 是否为中转 1.直达2.中转
                segments='[]' if not price_dif else json.dumps(price_dif),  # 中转时的各个航班信息
                getTime=time.time().__int__(),
            ))
            yield item

                # 获取直航白名单时用用
                # if not flag:
                #     flag = True
                #     with open(u'欧翼直航.csv', 'a+') as f:
                #         f.write('%s,%s\n' % (FROM, TO))

        # if item is None:
        #     # 设置失效
        #     params = {'carrier': 'EW'}
        #     _dates = [(datetime.strptime(_day, '%Y-%m-%d') - timedelta(num)).strftime('%Y%m%d') for num in (-1, 0, 1)]
        #     data_array = [{'depAirport': FROM, 'arrAirport': TO, 'date': _date} for _date in _dates]
        #     print(data_array)
        #     content = push_date(settings.PUSH_DATA_URL, params=params,
        #                         action='invalid', data_array=data_array)
        #     print('invalid : ' + str(content))

    # 请求最低价
    def get_data(self, FROM, TO):
        for i in range(2):
            lowfares_url = 'https://www.eurowings.com/services/lowfares.{}.{}.{:%m.%Y}.origindefault.en.promo.json'.format(
                FROM, TO, datetime.today() + relativedelta.relativedelta(months=i))
            while True:
                try:
                    response = requests.get(lowfares_url, timeout=180)
                except:
                    traceback.print_exc()
                    time.sleep(16)
                else:
                    result = json.loads(response.text)
                    data = result.get('days')
                    break
            yield data

    # 日期筛选优化
    def get_list(self, a_list):
        b_list = []
        for i in a_list:
            if i in b_list:
                continue
            b_list.append(i)
            if self.add_date(i, 1) in a_list:
                b_list.append(self.add_date(i, 1))
                b_list.append(self.add_date(i, 2))
            else:
                b_list.append(i)
                b_list.append(i)

        return b_list[1::3]

    # 简单的返回日期加运算
    @staticmethod
    def add_date(date, num):
        return (datetime.strptime(date, "%Y-%m-%d") + timedelta(num)).strftime("%Y-%m-%d")
