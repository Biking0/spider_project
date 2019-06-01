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
from lamudatech_dev import settings
from lamudatech_dev.pipelines import LamudatechDevPipeline

from utils.process_airport_city.get_airport_city import get_airport_city

# from utils.push_date import push_date


class AkSpider(scrapy.Spider):
    name = 'ak'
    spider_name = 'ak'
    start_urls = 'https://booking.airasia.com/Flight/Select?'
    version = 1.0

    errback_status = False
    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9",
            'Cache-Control': "no-cache",
            'Connection': "keep-alive",
            'Host': "booking.airasia.com",
            'Upgrade-Insecure-Requests': "1",
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        },

        DOWNLOADER_MIDDLEWARES={
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.AkProcessCookies': 500,
        },
        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 4,
        # DOWNLOAD_DELAY=3,
        DOWNLOAD_TIMEOUT=8,
        # COOKIES_ENABLED=False,
        HTTPERROR_ALLOWED_CODES=[403, 404],
        # LOG_FILE='log/%s-spider.log' % spider_name,
        # LOG_LEVEL='DEBUG',
        )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))
        while True:
            result = self.get_task(self.spider_name)
            airports, _date, _num = result[0].split(':')
            _from, _to = airports.split('-')
            print(result)
            # _from, _to = 'HKG', 'BKI'
            # _date = '{:%Y-%m-%d}'.format(datetime.today() + timedelta(3))
            for index, _date in enumerate(self._get_dates(_date, int(_num))):
                query = 'o1={_from}&d1={_to}&dd1={_date}&ADT=1&s=true&c=false'.format(_from=_from, _to=_to, _date=_date)
                total_url = self.start_urls + query
                if index == 0:
                    yield scrapy.Request(total_url, meta={'_from': _from, '_to': _to, 'origin': 1},
                                         )
                else:
                    yield scrapy.Request(total_url, meta={'_from': _from, '_to': _to},
                                         callback=self.parse, errback=self.errback
                                         )

    def errback(self, failure):
        if not self.errback_status:
            self.errback_status = True
        print('errback old proxy: %s' % failure.request.meta['proxy'])
        print(failure.value)
        return failure.request

    def parse(self, response):
        # meta = response.meta
        # _from = meta.get('_from')
        # _to = meta.get('_to')
        # _date = meta.get('_date')
        self.log(response.meta['proxy'])

        rows = response.xpath('//*[@id="availabilityForm"]//table[@class="table avail-table"]/tbody/tr[contains(@class, "-row")]')
        # 过滤中转航线
        nonstop_rows = [
            row for row in rows \
            if row.xpath(
                'td[contains(@class, "avail-table-vert")]//td[contains(@id, "icon_")]//td[@class="avail-table-detail"]/div/div'
            ).__len__() == 1
        ]
        for row in nonstop_rows:
            # 过滤仓位
            td_depart = row.xpath('td[contains(@class, "depart LF")]')

            for td in td_depart:
                item = FlightsItem()

                left_seats = td.xpath('div//div[@class="avail-table-seats-remaining"]/text()').extract_first()
                if left_seats:
                    left_seats = re.search(r'\d', left_seats).group()
                else:
                    left_seats = 6

                input_tag = td.xpath('div//input')
                value = input_tag.xpath('@value').extract_first()

                m = re.findall(r'~\w{3}~(\d{2}/\d{2}/\d{4} \d{2}:\d{2})', value)

                data_json = input_tag.xpath('@data-json').extract_first()
                result = json.loads(data_json)[0]
                carrier = result.get('brand')
                flightNumber = result.get('dimension16')
                depAirport = result.get('dimension2')
                arrAirport = result.get('dimension3')
                adultPrice = result.get('price')

                from_city = self.city_airport.get(depAirport, depAirport)
                to_city = self.city_airport.get(arrAirport, arrAirport)

                product = input_tag.xpath('@data-productclass').extract_first()
                cur = input_tag.xpath('@data-cur').extract_first()
                item.update(dict(
                    flightNumber=flightNumber,  # 航班号
                    depTime=time.mktime(time.strptime(m[0], "%m/%d/%Y %H:%M")).__int__(),  # 出发时间
                    arrTime=time.mktime(time.strptime(m[1], "%m/%d/%Y %H:%M")).__int__(),  # 达到时间
                    fromCity=from_city,  # 出发城市
                    toCity=to_city,  # 到达城市
                    depAirport=depAirport,  # 出发机场
                    arrAirport=arrAirport,  # 到达机场
                    currency=cur,  # 货币种类
                    adultPrice=adultPrice,  # 成人票价
                    adultTax=0,  # 税价
                    netFare=adultPrice,  # 净票价
                    maxSeats=left_seats,  # 可预定座位数
                    cabin=product,  # 舱位
                    carrier=carrier,  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments="NULL",  # 中转时的各个航班信息
                    getTime=time.mktime(datetime.now().timetuple()).__int__(),
                ))

                yield item

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_date, '%Y%m%d') + timedelta(day)).strftime('%Y-%m-%d'))
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
