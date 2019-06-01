# -*- coding: utf-8 -*-
import scrapy, requests, json, re, traceback
import time
from datetime import datetime, timedelta

# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from lamudatech_dev.items import FlightsItem
from lamudatech_dev import settings

from utils.process_airport_city.get_airport_city import get_airport_city

# from utils.airports_rd import get_airports
from utils.push_date import push_date
from lamudatech_dev.pipelines import LamudatechDevPipeline


class B5jSpider(scrapy.Spider):
    name = 'dg'
    spider_name = 'dg'
    start_urls = 'https://beta.cebupacificair.com/Mobile/Flight/Select?'
    search_seat = 9
    banned = False
    version = 1.1

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'accept': "application/json, text/javascript, */*; q=0.01",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'Cache-Control': "no-cache",
            'referer': 'https://beta.cebupacificair.com/Mobile/Flight/Search'
        },

        # 仅供测试用
        ITEM_PIPELINES={
            'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        },

        DOWNLOADER_MIDDLEWARES={
            'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.B5jProxyMiddleware': 401,
        },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        DOWNLOAD_DELAY=8,
        DOWNLOAD_TIMEOUT=8,
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
        permins = 0
        print(LamudatechDevPipeline.heartbeat(self.host_name, self.spider_name, self.num, permins, self.version))
        while True:
            result = self.get_task(self.spider_name)
            airports, _date, _num = result[0].split(':')
            # airports, _date, _num = 'DVO-TAG', '20181001', 30
            _from, _to = airports.split('-')

            for _date in self._get_dates(_date, int(_num)):
                params = parse.urlencode(dict(
                    o1=_from, d1=_to, o2='', dd1=_date, ADT=self.search_seat,
                    CHD=0, INF=0, inl=0, pos='cebu.ph', culture=''
                ))
                total_url = self.start_urls + params
                yield scrapy.Request(total_url,
                                     meta={'_from': _from, '_to': _to, '_date': _date},
                                     callback=self.parse,
                                     errback=self.errback)

    def errback(self, failure):
        if not self.banned:
            self.banned = True
        # print('errback old proxy: %s' % failure.request.meta['proxy'])
        self.log(failure.value, 40)
        return failure.request

    def parse(self, response):
        meta = response.meta
        _from = meta.get('_from')
        _to = meta.get('_to')
        _date = meta.get('_date')

        # 验证码
        if 'Are you human?' in response.body:
            self.banned = True
            self.log('\t\t be banned, retry...', 20)
            yield response.request
        # 解析页面
        else:
            self.log('available proxy: %s' % response.meta['proxy'], 20)

            self.banned = False
            from_city = self.city_airport.get(_from, _from)
            to_city = self.city_airport.get(_to, _to)

            tr_set = response.xpath('//*[@id="depart-table"]/tbody/tr[@class!="flight-legend"]')
            tr = [tr for tr in tr_set if tr.xpath('th/div').__len__() == 1]

            item = None
            for t in tr:
                item = FlightsItem()
                flight_number = re.sub(r'\s*', '',
                                       t.xpath('th//span[contains(@class, "flight-number")]/text()').extract_first())

                # 判断航线时间是否跨度两天
                sup = t.xpath('td[contains(@class, "visible-sm visible-xs")]/div//sup/text()').extract_first()
                if not sup:
                    dep_time, arr_time, _ = map(lambda x: re.sub(r'\s', '', x), t.xpath(
                        'td[contains(@class, "visible-sm visible-xs")]/div/div/text()').extract())
                    arr_date = _date
                else:
                    dep_time, arr_time, _, _ = map(lambda x: re.sub(r'\s', '', x), t.xpath(
                        'td[contains(@class, "visible-sm visible-xs")]/div/div/text()').extract())
                    arr_date = self._add_one(_date)

                dep_airport, arr_airport = t.xpath('td[@class="avail-table-vert text-center"]/div/div/text()').extract()
                # 价格详情
                label_l = t.xpath('td[contains(@class, "fare-bundle-radio-container")]/div/label')
                label = label_l[0]
                base_fare = label.xpath('@data-basefare').extract_first()
                tax = label.xpath('@data-webadminfee').extract_first()
                cabin = label.xpath('@data-fareclass').extract_first()
                currency, total_fare = (lambda x: (x[:3], x[3:]))(
                    re.sub(r'\s|,', '', label.xpath('text()').extract_first()))
                if not total_fare:
                    total_fare = 0.00
                    base_fare = 0.00
                    tax = 0.00
                    currency = ''
                segments = {
                    'F_B': 0,
                    'F_B_M': 0
                }
                try:
                    segments['F_B'] = re.sub(r'\s|,', '', label_l[1].xpath('text()').extract_first())
                    segments['F_B_M'] = re.sub(r'\s|,', '', label_l[2].xpath('text()').extract_first())
                except:
                    traceback.print_exc()
                    print('error')

                item.update(dict(
                    flightNumber=flight_number,  # 航班号
                    depTime=time.mktime(time.strptime(_date + dep_time, "%Y-%m-%d%H%MH")).__int__(),  # 出发时间
                    arrTime=time.mktime(time.strptime(arr_date + arr_time, "%Y-%m-%d%H%MH")).__int__(),  # 达到时间
                    fromCity=from_city,  # 出发城市
                    toCity=to_city,  # 到达城市
                    depAirport=dep_airport,  # 出发机场
                    arrAirport=arr_airport,  # 到达机场
                    currency=currency,  # 货币种类
                    adultPrice=float(total_fare),  # 成人票价
                    adultTax=float(tax),  # 税价
                    netFare=float(base_fare),  # 净票价
                    maxSeats=self.search_seat,  # 可预定座位数
                    cabin=cabin,  # 舱位
                    carrier=flight_number[:2],  # 航空公司
                    isChange=1,  # 是否为中转 1.直达2.中转
                    segments=json.dumps(segments),  # 中转时的各个航班信息
                    getTime=int(time.time()),
                ))

                yield item

            # 无数据，设置运价失效
            if not item:
                # 设置失效
                data = {'fromCity': _from, 'toCity': _to, 'date': _date}
                res = push_date(settings.PUSH_DATA_URL,
                          params={'carrier': self.spider_name},
                          action='invalid', data_array=[data])
                self.log('[%s] %s-%s no flights' % (_date, _from, _to), 20)
                # self.log(res, 20)

    @staticmethod
    def _add_one(_day):
        data = datetime.strptime(_day, '%Y-%m-%d') + timedelta(1)
        return data.strftime('%Y-%m-%d')

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
