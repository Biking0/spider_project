# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta

# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from lamudatech_dev.items import FlightsItem
from utils.process_airport_city.get_airport_city import get_airport_city
# from utils.airports_rd import get_airports
# from utils.push_date import push_date


class A0bSpider(scrapy.Spider):
    name = '0b'
    spider_name = '0b'
    start_urls = 'https://booking.blueairweb.com/{s}Flight/InternalSelect?'
    schedule = 'https://www.blueairweb.com/Schedule/{_from}{_to}.json?_={time}'
    search_seat = 5
    version = 1.0
    currency_cache = {
        u'€': u'EUR',
        u'$': u'USD',
        u'£': u'GBP',
    }

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Connection': "keep-alive",
            'Host': "booking.blueairweb.com",
            'Upgrade-Insecure-Requests': "1",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'Cache-Control': "no-cache",
            'Content-Type': "application/x-www-form-urlencoded"
        },

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        DOWNLOADER_MIDDLEWARES={
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
            # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
            'lamudatech_dev.middlewares.StatisticsItem': 400,
        },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        # DOWNLOAD_DELAY=3,
        # DOWNLOAD_TIMEOUT=6,
        # DEPTH_PRIORITY=1,
        # COOKIES_ENABLED=False,
        # HTTPERROR_ALLOWED_CODES=[403],
        # LOG_FILE='log/%s-spider.log' % spider_name,
        # LOG_LEVEL='DEBUG',
        )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        while True:
            result = self.get_task(self.spider_name)
            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')

            schedule_url = self.schedule.format(_from=_from, _to=_to, time=str(int(time.time() * 1000)))
            headers = {
                'Accept': "application/json, text/plain, */*",
                'Accept-Encoding': "gzip, deflate, br",
                'Accept-Language': "zh-CN,zh;q=0.9",
                'Connection': "keep-alive",
                'Host': "www.blueairweb.com",
                'Referer': "https://www.blueairweb.com/en/gb/",
                # 'Request-Context': "appId=cid-v1:000518ad-eea7-41cf-bb14-cfebafa3eea2",
                # 'Request-Id': "|3fsYf.1OJwy",
                'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
                'Cache-Control': "no-cache"
            }
            yield scrapy.Request(schedule_url, headers=headers,
                                 meta={'_from': _from, '_to': _to},
                                 callback=self.schedule_parse)

    # def errback(self, failure):
    #     self.log(failure.value, 40)
    #     time.sleep(8)
    #     return failure.request

    def schedule_parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        schedule = json.loads(response.text)
        available_dates = []
        for _date in schedule:
            if datetime.strptime(_date, "%Y-%m-%d") > datetime.today() + timedelta(31) or \
                    datetime.strptime(_date, "%Y-%m-%d") <= datetime.today():
                continue
            available_dates.append(_date)

        if available_dates:
            _date = available_dates.pop(0)
            params = {
                's': True, 'o1': _from, 'd1': _to, 'dd1': _date,
                'ADT': self.search_seat,
                'mon': True,
                'bpc': False,
                # 'bc': 'EUR'
            }
            total_url = self.start_urls.format(s='') + parse.urlencode(params)
            yield scrapy.Request(total_url,
                                 meta={'available_dates': available_dates,
                                       '_from': _from, '_to': _to, '_date': _date})

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        # _date = meta.get('_date')
        available_dates = meta.get('available_dates')

        if available_dates:
            session =  re.match(r'https://.*?/(.*?)/.*', response.url).group(1)
            for _date in available_dates:
                params = {
                    's': True, 'o1': _from, 'd1': _to, 'dd1': _date,
                    'ADT': self.search_seat,
                    'mon': True,
                    'bpc': False,
                    # 'bc': 'EUR'
                }
                total_url = self.start_urls.format(s=session+'/') + parse.urlencode(params)
                yield scrapy.Request(total_url,
                                     meta={'_from': _from, '_to': _to, '_date': _date})

        # 解析页面
        form_container = response.xpath('//div[@id="js_availability_container"]/form')

        div_fare_row = form_container.xpath('div[contains(@class, "fare-row")]')
        for fare_row in div_fare_row:
            div_outbound = fare_row.xpath('div[@data-class-index="0"]/div/div')
            # 售完跳过
            if not div_outbound:
                continue

            input_value = div_outbound.xpath('div[@class="fare-price-and-currency"]/input/@value').extract()
            flight_values = input_value[0].split('|')[1].split('~')
            # 过滤中转
            if '^' not in input_value[0]:
                flight_values = filter(lambda x:re.sub(r'\s*', '', x), flight_values)
                try:
                    carrier, flight_number, dep_airport, dep_date, arr_airport, arr_date = flight_values
                except Exception as e:
                    print(e)
                    print(flight_values)
                    continue
                fromCity = self.city_airport.get(dep_airport, dep_airport)
                toCity = self.city_airport.get(arr_airport, arr_airport)
                currency, price = re.match('(^\D*)?(.*)', input_value[2]).groups()
                price = re.sub(r',', '', price)
                currency = self.currency_cache.get(currency, currency)

                item = FlightsItem()
                item.update(dict(
                    flightNumber=carrier + flight_number.strip(),  # 航班号
                    depTime=int(time.mktime(time.strptime(dep_date, "%m/%d/%Y %H:%M"))),  # 出发时间
                    arrTime=int(time.mktime(time.strptime(arr_date, "%m/%d/%Y %H:%M"))),  # 达到时间
                    fromCity=fromCity,  # 出发城市
                    toCity=toCity,  # 到达城市
                    depAirport=dep_airport,  # 出发机场
                    arrAirport=arr_airport,  # 到达机场
                    currency=currency,  # 货币种类
                    adultPrice=float(price),  # 成人票价
                    adultTax=0,  # 税价
                    netFare=float(price),  # 净票价
                    maxSeats=self.search_seat,  # 可预定座位数
                    cabin='E',  # 舱位
                    carrier=carrier,  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="NULL",  # 中转时的各个航班信息
                    getTime=int(time.time()),
                ))

                yield item

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_date, '%Y%m%d') + timedelta(day)).strftime('%Y%m%d'))
        return dates

    def get_task(self, carrier):
        task_api = self.settings.get('GET_TASK_URL') + 'carrier=%s' % carrier
        while True:
            try:
                result = json.loads(requests.get(task_api, timeout=180).text).get('data')
            except Exception as e:
                self.log(e, 40)
                time.sleep(8)
            else:
                if not result:
                    self.log('Date is None!\nWaiting...', 40)
                    time.sleep(16)
                    continue
                break
        return result
