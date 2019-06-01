# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta

# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse
from lxml import etree
from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings

from utils.process_airport_city.get_airport_city import get_airport_city

# from utils.airports_rd import get_airports
from utils.push_date import push_date


class TrSpider(scrapy.Spider):
    name = 'tr'
    spider_name = 'tr'
    start_urls = 'https://makeabooking.flyscoot.com/Book/AvailabilityAjax?'
    base_url = 'https://makeabooking.flyscoot.com'
    banned = False
    version = 1.0

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'Cache-Control': "no-cache",
            'Content-Type': "application/x-www-form-urlencoded",
            'origin': "https://makeabooking.flyscoot.com",
            'referer': "https://makeabooking.flyscoot.com/",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        },

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        DOWNLOADER_MIDDLEWARES={
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.TrProcessCookies': 401,
        },

        CONCURRENT_REQUESTS=1,
        # DEPTH_PRIORITY=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        # DOWNLOAD_DELAY=3,
        DOWNLOAD_TIMEOUT=8,
        # COOKIES_ENABLED=False,
        # HTTPERROR_ALLOWED_CODES=[500],
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

            print(result)
            _date = re.sub(r'(\d{4})(\d{2})(\d{2})', r'\2/\3/\1', _date)
            payload = {
                'revAvailabilitySearch.SearchInfo.Direction': 'Oneway',
                'revAvailabilitySearch.SearchInfo.SearchStations[0].DepartureStationCode': _from,
                'revAvailabilitySearch.SearchInfo.SearchStations[0].ArrivalStationCode': _to,
                'revAvailabilitySearch.SearchInfo.SearchStations[0].DepartureDate': _date,
                'revAvailabilitySearch.SearchInfo.AdultCount': 1,
                'revAvailabilitySearch.SearchInfo.ChildrenCount': 0,
                'revAvailabilitySearch.SearchInfo.InfantCount': 0,
                'revAvailabilitySearch.SearchInfo.PromoCode': ''
            }
            body = parse.urlencode(payload)
            yield scrapy.Request(self.base_url, method='POST', body=body,
                                 meta={'_from': _from, '_to': _to, '_date': _date,
                                       '_num': _num, 'origin': 1},
                                 callback=self.parse,
                                 errback=self.errback
                                 )
            # 暂停引擎
            self.crawler.engine.pause()

    def errback(self, failure):
        self.log(failure.value, 40)
        self.banned = True
        # if not self.proxy:
        #     time.sleep(8)
        self.crawler.engine.unpause()
        # return failure.request

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        _date = meta.get('_date')
        _num = meta.get('_num')

        if '<title>WAF</title>' in response.text:
            self.log('<title>WAF</title> be banned. retry...', 40)
            self.banned = True
            # if not self.proxy:
            #     time.sleep(2)
            # yield response.request
        elif 'origin' in response.meta:
            headers = {
                'accept': "text/html, */*; q=0.01",
                'accept-encoding': "gzip, deflate, br",
                'accept-language': "zh-CN,zh;q=0.9",
                'referer': "https://makeabooking.flyscoot.com/Book/Flight",
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
                'x-distil-ajax': "ysbctttfwzatvbzercutdyvxzsasrf",
                'x-requested-with': "XMLHttpRequest",
                'Cache-Control': "no-cache"
            }

            for i, _date in enumerate(self._get_dates(_date, int(_num))):
                # if i == 0:
                #     continue
                params = parse.urlencode({
                    'AvailabilityAjax.LowFareMarketDate': '0|%s' % _date,
                    'AvailabilityAjax.Market': '%s|%s' % (_from, _to),
                })

                total_url = self.start_urls + params
                yield scrapy.Request(total_url,
                                     cookies=response.request.cookies,
                                     headers=headers,
                                     meta={'_from': _from, '_to': _to, '_date': _date},
                                     callback=self.parse,
                                     errback=self.errback
                                     )
        else:
            results = response.xpath('//*[@id="departure-results"]/div')

            item = None
            for departure_results in results:
                span = departure_results.xpath(
                    'div[@class="flight__stop"]//div[@class="flight-stop"]/span/text()').extract_first()
                # 跳过非直航
                if span != u'Direct Flight':
                    continue

                # 航空公司，航班号, 机场，时间
                _input = departure_results.xpath(
                    'div[@class="flight__upgrade-box"]//div[@data-fare="fly"]//input/@value').extract_first()

                # 经济舱优先
                if _input:
                    m = filter(lambda x: x, re.split(r'~|\s+', re.match(r'.*\|(.*)~$', _input).group(1)))
                    carrier, number, depAirport, date_from, time_from, arrAirport, date_to, time_to = m
                    flightNumber = carrier + number
                    price = departure_results.xpath(
                        'div[@class="flight__fly"]//span[contains(@class, "price--sale")]/text()').extract()
                    cabin = 'E'

                    # 出发，到达时间
                    depTime = time.mktime(time.strptime(date_from + time_from, "%m/%d/%Y%H:%M")).__int__()
                    arrTime = time.mktime(time.strptime(date_to + time_to, "%m/%d/%Y%H:%M")).__int__()

                    # 座位
                    seats = departure_results.xpath('div[@class="flight__fly"]/p/text()').extract_first()
                    left_seats = seats[:1] if seats else 10

                # 商务舱
                else:
                    # 机场
                    depAirport = departure_results.xpath('div[@class="flight__from"]/ul/li/text()').extract_first()[:3]
                    arrAirport = departure_results.xpath('div[@class="flight__to"]/ul/li/text()').extract_first()[:3]

                    # 航空公司，航班号
                    data_content = departure_results.xpath(
                        'div[@class="flight__stop"]/div[@role="button"]/@data-content').extract_first()
                    data_xml = etree.HTML(data_content)
                    p = data_xml.xpath('//p/text()')[0]
                    flightNumber = re.sub(r'\s*', '', re.match(r'Departing Flight:(.*)\(Scoot\)', p).group(1))
                    carrier = flightNumber[:2]

                    # 出发，到达时间
                    li = data_xml.xpath('//ul/li/text()')
                    time_from, time_to = map((lambda x: re.match(r'\w+: (.*?)\).*', x).group(1)), li[:2])
                    depTime = time.mktime(time.strptime(time_from, "%H:%M%p (%a, %d %b %Y")).__int__()
                    arrTime = time.mktime(time.strptime(time_to, "%H:%M%p (%a, %d %b %Y")).__int__()

                    price = departure_results.xpath(
                        'div[@class="flight__scootbiz visible-xs"]//span[contains(@class, "price--sale")]/text()').extract()
                    cabin = 'S'

                    # 座位
                    seats = departure_results.xpath('div[@class="flight__scootbiz visible-xs"]/p/text()').extract_first()
                    left_seats = seats[:1] if seats else 10

                # 货币种类，价格，座位
                if len(price) == 1:
                    currency = price[0][:3]
                    adultPrice = float(price[0][3:].replace(',', ''))

                elif len(price) == 2:
                    # 换行
                    currency = price[0]
                    adultPrice = float(price[1].replace(',', ''))

                else:
                    continue

                from_city = self.city_airport.get(depAirport, depAirport)
                to_city = self.city_airport.get(arrAirport, arrAirport)

                item = FlightsItem()
                item.update(dict(
                    flightNumber=flightNumber,
                    depTime=depTime,  # 出发时间
                    arrTime=arrTime,  # 达到时间
                    fromCity=from_city,  # 出发城市
                    toCity=to_city,  # 到达城市
                    depAirport=depAirport,  # 出发机场
                    arrAirport=arrAirport,  # 到达机场
                    currency=currency,  # 货币种类
                    adultPrice=adultPrice,  # 成人票价
                    adultTax=0,  # 税价
                    netFare=adultPrice,  # 净票价
                    maxSeats=left_seats,  # 可预定座位数
                    cabin=cabin,  # 舱位
                    carrier=carrier,  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="NULL",  # 中转时的各个航班信息
                    getTime=time.time().__int__(),
                ))
                yield item

            # 无航班设置失效
            if not item:
                data = {
                    'fromCity': _from,
                    'toCity': _to,
                    'date': re.sub(r'(\d+)/(\d+)/(\d+)', r'\3\1\2', _date),
                }
                res = push_date(settings.PUSH_DATA_URL, {'carrier': 'TR'}, 'invalid', [data])
                self.log('%s-%s: %s no flights' % (_from, _to, _date), 20)

        self.crawler.engine.unpause()

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_date, '%m/%d/%Y') + timedelta(day)).strftime('%m/%d/%Y'))
        return dates

    def get_task(self, carrier):
        task_api = settings.GET_TASK_URL + 'carrier=%s' % carrier
        try:
            result = json.loads(requests.get(task_api, timeout=180).text).get('data')
        except Exception as e:
            self.log(e, 40)
            result = None
        if not result:
            self.log('Date is None!\nWaiting...', 40)
            time.sleep(16)
        return result
