# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta

from scrapy.http.response.html import HtmlResponse

# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings

from utils.process_airport_city.get_airport_city import get_airport_city

# from utils.airports_rd import get_airports
# from utils.push_date import push_date


class HvSpider(scrapy.Spider):
    name = 'hv'
    spider_name = 'hv'
    version = 1.0
    start_urls = 'https://www.transavia.com/en-EU/book-a-flight/flights/multidayavailability/'
    select_url = 'https://www.transavia.com/en-EU/book-a-flight/flights/SingleDayAvailability/'

    currency_cache = {
        u'€': u'EUR',
        u'$': u'USD',
        u'£': u'GBP',
    }

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'Content-Type': "application/x-www-form-urlencoded",
            'origin': "https://www.transavia.com",
            'referer': "https://www.transavia.com/en-EU/book-a-flight/flights/search/",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'x-distil-ajax': "xfuvwdyw",
            'x-newrelic-id': "VwcFUFBACQAIV1dTAgI=",
            'x-requested-with': "XMLHttpRequest",
            'Cache-Control': "no-cache"
        },

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        DOWNLOADER_MIDDLEWARES={
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
            'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.HvProcessCookies': 401,
        },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        # DOWNLOAD_DELAY=3,
        DOWNLOAD_TIMEOUT=16,
        # COOKIES_ENABLED=False,
        # HTTPERROR_ALLOWED_CODES=[405],
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
            print(result)
            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')

            for _date in self._get_dates(_date, int(_num)):
                body = {
                    'selectPassengersCount.AdultCount': 3,
                    'selectPassengersCount.ChildCount': 0,
                    'selectPassengersCount.InfantCount': 0,
                    'routeSelection.DepartureStation': _from,
                    'routeSelection.ArrivalStation': _to,
                    'dateSelection.OutboundDate.Day': int(_date[6:]),
                    'dateSelection.OutboundDate.Month': int(_date[4:6]),
                    'dateSelection.OutboundDate.Year': int(_date[:4]),
                    'dateSelection.InboundDate.Day': '',
                    'dateSelection.InboundDate.Month':'',
                    'dateSelection.InboundDate.Year':'',
                    'dateSelection.IsReturnFlight': False,
                    'flyingBlueSearch.FlyingBlueSearch': False,
                }
                yield scrapy.Request(self.start_urls, method='POST', body=json.dumps(body),
                                     meta={'_from': _from, '_to': _to, '_date': _date,
                                           'origin': 1},
                                     # callback=self.parse,
                                     # errback=self.errback
                                     )

    # def errback(self, failure):
    #     self.log(failure.value, 40)
    #     time.sleep(8)
    #     return failure.request

    def parse(self, response):
        # meta = response.meta
        # _from = meta.get('_from')
        # _to = meta.get('_to')
        # _date = meta.get('_date')

        res = json.loads(response.text)
        if 'origin' in response.meta:
            multiDayAvailabilityOutbound = res['multiDayAvailabilityOutbound']
            r = HtmlResponse(url=self.start_urls, body=multiDayAvailabilityOutbound.encode('utf-8'))
            __RequestVerificationToken = r.xpath('//div[@class="animation-container"]//input[@name="__RequestVerificationToken"]/@value').extract_first()
            li_days = r.xpath('//*[@class="HV-gc bulletless days"]/li/div[@class="day day-with-availability"]')
            for li in li_days:
                date_date = li.xpath('@data-date').extract_first()
                body = {
                    'selectSingleDayAvailability.JourneyType': 'OutboundFlight',
                    'selectSingleDayAvailability.Date.DateToParse': date_date[:10],
                    'selectSingleDayAvailability.AutoSelect': False,
                    '__RequestVerificationToken': __RequestVerificationToken
                }
                yield scrapy.Request(self.select_url, method='POST',
                                     body=parse.urlencode(body),
                                     headers=response.request.headers,
                                     cookies=response.request.cookies,
                                     )

        else:
            SingleDayOutbound = res['SingleDayOutbound']
            html = HtmlResponse(url='', body=SingleDayOutbound.encode('utf-8'))
            buttons = html.xpath('//button[@class="flight-result-button"]')
            for button in buttons:
                # 机场
                button_value = button.xpath('@value').extract_first()
                dep_airport, arr_airport = re.findall(r'~(\w{3})~', button_value)[:2]
                fromCity = self.city_airport.get(dep_airport, dep_airport)
                toCity = self.city_airport.get(arr_airport, arr_airport)
                # 时间
                div_times = button.xpath('div[@class="times"]')
                departure = div_times.xpath('time[@class="departure"]/@datetime').extract_first()
                departure_time = div_times.xpath('time[@class="departure"]/text()').extract_first().strip()
                dep_date = "%s %s:00" % (departure[:10], departure_time)
                arrival = div_times.xpath('time[@class="arrival"]/@datetime').extract_first()
                arrival_time = div_times.xpath('time[@class="arrival"]/text()').extract_first().strip()
                arr_date = "%s %s:00" % (arrival[:10], arrival_time)
                # 航班号
                details = button.xpath('div[@class="details"]')
                flight_number_list = details.xpath('ul/li[@class="flight-number"]/text()').extract()
                flight_number = flight_number_list[1].strip()
                # 价格
                actions = button.xpath('div[@class="actions"]')
                price_div = actions.xpath('div[contains(@class, "price")]')
                currency = price_div.xpath('span[@class="currency"]/text()').extract_first().strip()
                currency = self.currency_cache.get(currency, currency)
                price = price_div.xpath('text()[2]').extract_first().strip()

                item = FlightsItem()
                item.update(dict(
                    flightNumber=flight_number,  # 航班号
                    depTime=int(time.mktime(time.strptime(dep_date, "%d/%m/%Y %H:%M:%S"))),  # 出发时间
                    arrTime=int(time.mktime(time.strptime(arr_date, "%d/%m/%Y %H:%M:%S"))),  # 达到时间
                    fromCity=fromCity,  # 出发城市
                    toCity=toCity,  # 到达城市
                    depAirport=dep_airport,  # 出发机场
                    arrAirport=arr_airport,  # 到达机场
                    currency=currency,  # 货币种类
                    adultPrice=float(price),  # 成人票价
                    adultTax=0,  # 税价
                    netFare=float(price),  # 净票价
                    maxSeats=3,  # 可预定座位数
                    cabin='E',  # 舱位
                    carrier=flight_number[:2],  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="NULL",  # 中转时的各个航班信息
                    getTime=int(time.time()),
                ))

                yield item

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(3, _num+3, 7):
            dates.append((datetime.strptime(_date, '%Y%m%d') + timedelta(day)).strftime('%Y%m%d'))
        return dates

    def get_task(self, carrier):
        task_api = settings.GET_TASK_URL + 'carrier=%s' % carrier
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
