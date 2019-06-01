# -*- coding: utf-8 -*-
import scrapy, re, json, time, requests, logging
from datetime import datetime, timedelta
from itertools import groupby

from utils.process_airport_city.get_airport_city import get_airport_city
from lamudatech_dev import settings
from lamudatech_dev.items import FlightsItem
from lamudatech_dev.pipelines import LamudatechDevPipeline

try:
    from urlparse import parse_qs
except ImportError:
    from urllib.parse import parse_qs


class LxSpider(scrapy.Spider):
    name = 'lx'
    spider_name = 'lx'
    version = 1.0

    start_urls = 'https://www.swiss.com'
    is_ok = True

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS = {
            'accept': "*/*",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'x-distil-ajax': "dcquuxsbfeyeruwwzcwzwfxauzafwvsdrxzxs",
            'x-requested-with': "XMLHttpRequest",
            'Cache-Control': "no-cache",
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:59.0) Gecko/20100101 Firefox/59.0',
        },

        DOWNLOADER_MIDDLEWARES = {
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.LxProcessCookies': 500,
        },

        # 仅供测试用
        # ITEM_PIPELINES = {
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        DEPTH_PRIORITY=1,
        CONCURRENT_REQUESTS = 1,
        CLOSESPIDER_TIMEOUT = 60 * 60 * 2,
        # HTTPERROR_ALLOWED_CODES = [405],
        # DOWNLOAD_DELAY = 3,
        # DOWNLOAD_TIMEOUT = 6,
        # LOG_FILE = 'log/%s-spider.log' % spider_name,
        # LOG_LEVEL = 'DEBUG',
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))
        while True:
            try:
                data_api = settings.GET_TASK_URL + 'carrier=LX'
                result = json.loads(requests.get(data_api, timeout=180).text).get('data')
            except Exception as e:
                self.log(e)
                result = None

            if not result:
                self.log('Date is None!', level=20)
                self.log('Waiting...', level=20)
                time.sleep(16)
                continue

            print(result)
            airports, _date, _num = result[0].split(':')
            FROM, TO = airports.split('-')
            # 日期后移3天
            _date = datetime.strftime(datetime.strptime(_date, "%Y%m%d") + timedelta(3), "%Y-%m-%d")

            path_url = '/us/en/Book/Outbound/{FROM}-{TO}/from-{_date}/adults-1/children-0/infants-0/class-economy'.format(
                FROM=FROM, TO=TO, _date=_date)
            total_url = self.start_urls + path_url

            yield scrapy.Request(url=total_url,
                                 meta={
                                     'origin': 1,
                                 },
                                 callback=self.parse,
                                 dont_filter=True,
                                 errback=lambda x: self.download_errback(x, total_url)
                                 )
            # 暂停爬虫引擎
            self.crawler.engine.pause()

    def download_errback(self,x,url):
        logging.info('error download:' + url)
        self.is_ok = False

    def parse(self, response):
        meta = response.meta
        self.is_ok=True

        # 解析items
        div_list = response.xpath(
            '//*[@id="frm-matrix"]/div[2]/div[contains(@class, "book_bundle_row") and not(contains(@class, "has-multiflight"))]')

        item = None
        items = list()
        flight_date = None
        for div in div_list:
            row_header = div.xpath('div[@class="book_bundle_row--header"]')
            # 取出日期用于后面时间戳计算
            h3 = row_header.xpath('div[@class="is-visuallyhidden"]/h3/text()').extract_first()
            # u'Sunday 08/04/2018, London (LHR) ab 12:05, Zurich (ZRH) an 14:45.  Economy from GBP 228.  Business from not available. Operated by SWISS GLOBAL AIR LINES. '
            flight_date = re.match(r'\w+\s+(.*?),.*', h3).group(1)

            flightentry = row_header.xpath(
                'div[@class="book_bundle_row--flightinfo"]/div[@class="book-bundle-flightentry"]')

            # 机场，时间
            flightentry_time = flightentry.xpath('div[@class="book-bundle-flightentry--time"]')
            # 出发机场，时间
            departure = flightentry_time.xpath('div[@class="book-bundle-flightentry--departure"]')
            depAirport = departure.xpath('text()').extract_first().strip()
            dep_time = departure.xpath('strong/text()').extract_first().strip()
            dep_data = flight_date + dep_time
            # 到达机场，时间
            arrival = flightentry_time.xpath('div[@class="book-bundle-flightentry--arrival"]')
            arrAirport = arrival.xpath('text()').extract_first().strip()
            arr_time = arrival.xpath('strong/text()').extract_first().strip()
            sub = arrival.xpath('strong/sub/text()').extract_first()
            arr_date = flight_date + arr_time
            if sub:
                arr_date = self.add_date(arr_date, int(sub))

            # 城市
            fromCity = self.city_airport.get(depAirport, depAirport)
            toCity = self.city_airport.get(arrAirport, arrAirport)

            flightentry_info = flightentry.xpath(
                'div[@class="book-bundle-flightentry--info"]/div[@class="book-bundle-flightentry--metainfo"]')
            # 航班号
            flightentry_number = flightentry_info.xpath(
                'a[@class="book-bundle-flightentry--number"]/text()').extract_first()
            flightNumber = re.sub(r'\s*', '', flightentry_number)

            # # 过滤共享航班
            # flightentry_operator = flightentry_info.xpath(
            #     'span[@class="book-bundle-flightentry--operator"]/text()').extract_first()
            # if 'SWISS' in flightentry_operator:
            #     pass
            # else:
            #     continue

            buttons = row_header.xpath('div[@class="book_bundle_row--buttons"]')
            li_list = buttons.xpath('div/ul/li')
            for li in li_list:
                li_button = li.xpath('button')
                if li_button:
                    span = li_button.xpath('span/text()').extract()
                    cabin, currency, price, _ = span
                    currency = re.match(r'from\s(.*)', currency).group(1)
                    if currency == u'¥':
                        currency = u'CNY'
                    price = re.sub(r'\W', '', price)
                else:
                    # 跳过已售完仓位
                    continue

                # 剩余座位
                div_text = li.xpath('div/text()').extract_first()
                if div_text:
                    left_seats = re.match(r'.*(\d).*', div_text, flags=re.DOTALL).group(1)
                else:
                    left_seats = 9

                item = FlightsItem()
                item.update(dict(
                    flightNumber=flightNumber,  # 航班号
                    depTime=int(time.mktime(time.strptime(dep_data, "%d/%m/%Y%H:%M"))),  # 出发时间
                    arrTime=int(time.mktime(time.strptime(arr_date, "%d/%m/%Y%H:%M"))),  # 达到时间
                    fromCity=fromCity,  # 出发城市
                    toCity=toCity,  # 到达城市
                    depAirport=depAirport,  # 出发机场
                    arrAirport=arrAirport,  # 到达机场
                    currency=currency[-3:],  # 货币种类
                    adultPrice=float(price),  # 成人票价
                    adultTax=0,  # 税价
                    netFare=float(price),  # 净票价
                    maxSeats=left_seats,  # 可预定座位数
                    cabin=cabin,  # 舱位
                    carrier=flightNumber[:2],  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="NULL",  # 中转时的各个航班信息
                    getTime=int(time.time()),
                ))
                # 比价
                items.append(item)

        # 按航班号分组，返回最低价
        items = sorted(items, key=lambda x: x['flightNumber'])
        items_group = groupby(items, key=lambda x: x['flightNumber'])
        for k, g in items_group:
            yield min(g, key=lambda x: x['adultPrice'])

        # 解析url
        if 'origin' in meta and flight_date is not None:
            a_list = response.xpath('//*[@id="matrixDaySelection"]/ul/li/a[@data-has-module="yes"]/@href').extract()
            # 剔除模拟爬过的页面
            a_list_s = [link for link in a_list if parse_qs(link.split('?')[1])['selectedDate'][0] != flight_date ]
            for url_path in a_list_s:
                total_url = self.start_urls + url_path
                yield scrapy.Request(total_url,
                                     cookies=response.request.cookies,
                                     callback=self.parse,
                                     dont_filter=True
                                     )
        # 恢复引擎
        self.crawler.engine.unpause()

    @staticmethod
    def add_date(date, num):
        return datetime.strftime(datetime.strptime(date, "%d/%m/%Y%H:%M") + timedelta(num), "%d/%m/%Y%H:%M")

    # @staticmethod
    # def _get_dates():
    #     dates = []
    #     for day in range(3, 32, 7):
    #         dates.append((datetime.utcnow() + timedelta(day)).strftime('%Y-%m-%d'))
    #     return dates
