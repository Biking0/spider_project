# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta

# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from scrapy.http import HtmlResponse
from lamudatech_dev.items import FlightsItem
from utils.process_airport_city.get_airport_city import get_airport_city
# from utils.airports_rd import get_airports
from utils.push_date import push_date


class LsSpider(scrapy.Spider):
    name = 'ls'
    spider_name = 'ls'
    start_urls = 'https://www.jet2.com/en/cheap-flights/'
    version = 1.1
    is_ok = True

    abc_cache = {
        'CPH': 'Copenhagen', 'BCN': 'Barcelona', 'EDI': 'Edinburgh', 'EMA': 'East', 'ACE': 'Lanzarote', 'GLA': 'Glasgow',
        'NAP': 'Naples', 'ILD': 'Lleida', 'ZTH': 'Zante', 'REU': 'Reus', 'GNB': 'Grenoble', 'BOJ': 'Bourgas',
        'FUE': 'Fuerteventura', 'FNC': 'Madeira', 'MUC': 'Munich', 'AYT': 'Antalya', 'EGC': 'Bergerac', 'AGP': 'Malaga',
        'SKG': 'Thessaloniki', 'PRG': 'Prague', 'SXF': 'Berlin', 'LYS': 'Lyon', 'MAN': 'Manchester', 'SZG': 'Salzburg',
        'IBZ': 'Ibiza', 'LBA': 'Leeds', 'RMU': 'Murcia', 'FAO': 'Faro', 'PSA': 'Pisa', 'AMS': 'Amsterdam',
        'PMI': 'Majorca', 'BUD': 'Budapest', 'FCO': 'Rome', 'JER': 'Jersey', 'MLA': 'Malta', 'VCE': 'Venice',
        'HER': 'Crete', 'TRN': 'Turin', 'STN': 'london-stansted', 'GVA': 'Geneva', 'SPU': 'Split', 'DLM': 'Dalaman',
        'LRH': 'Rochelle', 'BFS': 'Belfast', 'CHQ': 'Crete', 'MJV': 'Murcia', 'ADB': 'Izmir', 'VRN': 'Verona',
        'MAH': 'Menorca', 'GRO': 'Girona', 'LPA': 'Gran', 'KGS': 'Kos', 'CDG': 'Paris', 'VIE': 'Vienna', 'KRK': 'Krakow',
        'LEI': 'Almeria', 'EWR': 'New', 'CGN': 'Cologne', 'ALC': 'Alicante', 'PFO': 'Paphos', 'BJV': 'Bodrum',
        'BHX': 'Birmingham', 'NCL': 'Newcastle', 'PUY': 'Pula', 'RHO': 'Rhodes', 'LCA': 'Larnaca', 'EFL': 'Kefalonia',
        'CFU': 'Corfu', 'NCE': 'Nice', 'TFS': 'Tenerife', 'DBV': 'Dubrovnik'
    }

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'Cache-Control': "no-cache",
            'referer': 'https://www.jet2.com/',
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        },

        DOWNLOAD_TIMEOUT=20,

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        DOWNLOADER_MIDDLEWARES={
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
            # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.ProxyMiddleware':300,
        },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        # DEPTH_PRIORITY=1,
        # DOWNLOAD_DELAY=3,
        # DOWNLOAD_TIMEOUT=6,
        # COOKIES_ENABLED=False,
        # COOKIES_DEBUG=False,
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

            _from = self.abc_cache.get(_from, _to)
            _to = self.abc_cache.get(_to, _to)
            _date = re.sub(r'(\d{4})(\d{2})(\d{2})', r'\1-\2-\3', _date)
            params = '{_from}/{_to}?from={_date}&adults=5&children&infants=0&preselect=true'.format(
                _date=_date, _from=_from, _to=_to)
            total_url = parse.basejoin(self.start_urls, params)

            yield scrapy.Request(total_url, meta={'origin': 1},
                                    errback=self.errback,
                                    callback=self.parse)

    def errback(self, failure):
        self.log(failure.value, 40)
        self.is_ok = False
        # time.sleep(8)
        return failure.request

    def parse(self, response):
        meta = response.meta
        # _from = meta.get('_from')
        # _to = meta.get('_to')
        # _date = meta.get('_date')

        self.is_ok = True
        if 'origin' in meta:
            scid = response.xpath('//a[@class="logout__name"]/@href').re_first(r'.*scid=(.*)')
            dsid = response.xpath('//div[@class="flight-results__wrapper clearfix"]/@data-dsid').extract_first()

            set_cookies = response.headers.getlist('Set-Cookie')
            cookie_items = [re.match(r'(.*?)=(.*?);', i).groups() for i in set_cookies]
            cookies = []
            for k, v in cookie_items:
                cookie = {u'domain': u'.jet2.com', u'secure': False, u'value': unicode(v), u'expiry': None,
                          u'path': u'/', u'httpOnly': False, u'name': unicode(k)}
                cookies.append(cookie)

            flight_search_url = 'https://www.jet2.com/api/search/flightsearchresults/update?scid=' + scid

            headers = {
                'accept-encoding': "gzip, deflate, br",
                'accept-language': "zh-CN,zh;q=0.9",
                'adrum': "isAjax:true",
                'content-type': "application/json; charset=UTF-8",
                'origin': "https://www.jet2.com",
                'referer': response.url,
                'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
                'x-requested-with': "XMLHttpRequest",
                'Cache-Control': "no-cache"
            }

            td_date = response.xpath('//tbody[@class="calendar__body"]/tr/td[@class="calendar__day "]')
            for td in td_date:
                flight_id = td.xpath('@data-cheapest-flight-id').extract_first()
                data_date = td.xpath('@data-date').extract_first()
                if datetime.strptime(data_date, "%Y-%m-%d") > datetime.today() + timedelta(31):
                    continue
                body = {"isCalendarSelection": True, "flightId": flight_id, "date": data_date,
                        "isOutbound": True, "isFull": False, "datasource": dsid}

                yield scrapy.Request(flight_search_url, method='POST',
                                     headers=headers, cookies=cookies,
                                     body=json.dumps(body),
                                     errback=self.errback,
                                     callback=self.parse)
        else:
            json_data = json.loads(response.text)
            # 如果是最后一页停止请求，防止死循环
            if 'end' not in response.meta:
                html = json_data['Data']['Html']
                r = HtmlResponse('', body=html.encode('utf-8'))
                flight_ids = r.xpath('//div[@class="times-summary__item "]/@data-flight-id').extract()
                request_body = json.loads(response.request.body)
                # 如果当前页面有多个航班继续请求
                request_body.pop('date')
                for flight_id in flight_ids:
                    request_body.update({'flightId': flight_id, 'isCalendarSelection': False})
                    yield scrapy.Request(response.url, method='POST',
                                         headers=response.request.headers, 
                                         cookies=response.request.cookies,
                                         body=json.dumps(request_body),
                                         meta={'end': 1},
                                         callback=self.parse,
                                         errback=self.errback)

            # 解析json数据
            products = json_data['Gtm']['ecommerce']['click']['products']
            products_0 = products[0]
            flight_number = products_0['dimension6']
            _, dep_date, _, arr_date = products_0['dimension57'].split('_')
            currency = products_0['dimension17']
            dep_airport = products_0['dimension4']
            arr_airport = products_0['dimension9']
            price = products_0['price']

            fromCity = self.city_airport.get(dep_airport, dep_airport)
            toCity = self.city_airport.get(arr_airport, arr_airport)

            item = FlightsItem()
            item.update(dict(
                flightNumber=flight_number,  # 航班号
                depTime=int(time.mktime(time.strptime(dep_date, "%Y-%m-%dT%H:%M:%S"))),  # 出发时间
                arrTime=int(time.mktime(time.strptime(arr_date, "%Y-%m-%dT%H:%M:%S"))),  # 达到时间
                fromCity=fromCity,  # 出发城市
                toCity=toCity,  # 到达城市
                depAirport=dep_airport,  # 出发机场
                arrAirport=arr_airport,  # 到达机场
                currency=currency,  # 货币种类
                adultPrice=price,  # 成人票价
                adultTax=0,  # 税价
                netFare=price,  # 净票价
                maxSeats=5,  # 可预定座位数
                cabin='E',  # 舱位
                carrier=flight_number[:2],  # 航空公司
                isChange=1,  # 是否为中转 1.直达2.中转
                segments="NULL",  # 中转时的各个航班信息
                getTime=int(time.time()),
            ))

            yield item

    # @staticmethod
    # def _get_dates(_date, _num):
    #     dates = []
    #     for day in range(0, _num):
    #         dates.append((datetime.strptime(_date, '%Y%m%d') + timedelta(day)).strftime('%Y%m%d'))
    #     return dates

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
