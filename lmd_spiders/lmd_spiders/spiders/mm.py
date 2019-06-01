# -*- coding: utf-8 -*-
import scrapy, logging, time, json, re
from datetime import datetime, timedelta
from utils.spe_util import vyUtil
from utils import pubUtil, dataUtil
from lmd_spiders.items import LmdSpidersItem
from lmd_spiders import settings


class MmSpider(scrapy.Spider):
    name = 'mm'
    allowed_domains = ['flypeach.com']
    start_urls = ['https://booking.flypeach.com/en',
                    'https://booking.flypeach.com/en/flight_search']
    carrier = 'MM'
    isOK = False
    version = 1.0
    task = []
    currency_cache = {
        u'₩': u'KRW', # 韩元
        u'￥': u'JPY', # 日元
        u'THB': u'THB',
        u'HK$': u'HKD', # 港币
        u'NT$': u'TWD', # 台币
        u'CNY': u'CNY',
    }

    custom_settings = dict(

        DEFAULT_REQUEST_HEADERS = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Mobile Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cache-Control": "max-age=0",
            "Content-Type": "application/x-www-form-urlencoded",
            "Host": "booking.flypeach.com",
            "Origin": "https://booking.flypeach.com",
            "Referer": "https://booking.flypeach.com/pc/en",
            "Upgrade-Insecure-Requests": "1",
            "Connection": "keep-alive",
            "Cookie": "name=lcc"
        },

        # DEFAULT_POST_DATA = { # 如需测试某航线，只需把下面三行注释放开并按照下面格式修改为对应的内容即可
        #     # "flight_search_parameter[0][departure_date]": "2018/07/15",
        #     # "flight_search_parameter[0][departure_airport_code]": "PUS",
        #     # "flight_search_parameter[0][arrival_airport_code]": "KIX",
        #     "flight_search_parameter[0][is_return]": "False",
        #     "flight_search_parameter[0][return_date]": "",
        #     "adult_count": "3",
        #     "child_count": "0",
        #     "infant_count": "0",
        #     "r": "static_search",
        # },

         DEFAULT_POST_DATA = { # 如需测试某航线，只需把下面三行注释放开并按照下面格式修改为对应的内容即可
            # "flight_search_parameter[0][departure_date]": "2018/07/15",
            # "flight_search_parameter[0][departure_airport_code]": "PUS",
            # "flight_search_parameter[0][arrival_airport_code]": "KIX",
            "flight_search_parameter[0][is_return]": False,
            "flight_search_parameter[0][return_date]": "",
            "adult_count": 3,
            "child_count": 0,
            "infant_count": 0,
            "r": "static_search",
        },

        PROXY_TRY_NUM = 2,

        DOWNLOAD_TIMEOUT=40,

        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        COOKIES_ENABLED=True,
        CONCURRENT_REQUESTS=1,
        DOWNLOADER_MIDDLEWARES={
            'lmd_spiders.middlewares.StatisticsItem': 200,
            # 'lmd_spiders.middlewares.ProxyMiddleware': 300,
            'lmd_spiders.middlewares.MmCookieMiddleware': 300,
        },

        # ITEM_PIPELINES={ # 往测试库添加数据
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },

    )

    def __init__(self, *args, **kwargs):
        super(MmSpider, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.carrier, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl(self.carrier, 5)
            if not result:
                logging.info('get task error')
                time.sleep(3)
                continue
            for data in result:
                (_dt, dep, to, days) = vyUtil.analysisData(data)
                for i in range(int(days)):

                    dt = (datetime.strptime(_dt, '%Y%m%d') + timedelta(days=i)).strftime('%Y/%m/%d')
                    self.task.append({'date':dt.replace('/', ''),
                                    'depAirport': dep,
                                    'arrAirport': to,
                                    'mins': settings.INVALID_TIME
                                    })
                    post_data = {
                        "flight_search_parameter[0][departure_date]": dt,
                        "flight_search_parameter[0][departure_airport_code]": dep,
                        "flight_search_parameter[0][arrival_airport_code]": to,
                    }
                    post_data.update(self.custom_settings.get('DEFAULT_POST_DATA'))
                    # print(post_data)
                    yield scrapy.Request(
                        url=self.start_urls[1],
                        method="GET",
                        # body=json.dumps(post_data),
                        # formdata=post_data,
                        meta={'post_data': post_data},
                        dont_filter=True,
                        callback=self.parse,
                        errback=self.errback,
                    )
    
    def en_parse(self, response):
        # print(response.body)
        cookies = response.headers.getlist('Set-Cookie')
        print('res.heades.getli("Cookie"): %s' % response.headers.getlist("Cookie"))
        print('res.req.heades.getli("Cookie"): %s' % response.request.headers.getlist("Cookie"))
        print('res.req.cookies: %s' % response.request.cookies)
        print('res.headers.getlist(Set-Cookie): %s' % response.headers.getlist('Set-Cookie'))
        if not cookies or len(cookies) == 0:
            # print(cookies)
            self.log('get_cookies error', 20)
            # yield response.request
        else:
            # print(cookies)
            # print(len(cookies))
            cookie = cookies[0]
            cookie_dict = dict()
            for cookie in cookies:
                cookie_li = cookie.split(';')
                ci = cookie_li[0]
                k, v = ci.split('=')
                cookie_dict[k] = v
            print(cookie_dict)
            yield scrapy.Request(
                url=self.start_urls[1],
                cookies=cookie_dict,
                dont_filter=True,
                callback=self.parse,
                # errback=self.errback,
            )

    def errback(self, failure):
        self.log(failure.value, 40)
        self.is_ok = False
        # time.sleep(8)
        return failure.request

    def parse(self, response):
        html_content = response.body
        html_content = html_content.decode("utf-8")  # 获取网页数据
        # print(html_content)

        try:
            flight_results = re.search(r"var flightResults = (.*);", html_content)
            flight_data = flight_results.group(1)
            flight_data = json.loads(flight_data)[0]
        except:
            # print(html_content)
            self.log(html_content, 30)
            # yield response.request
            return
        currency_flag = re.search(r"'initCurrency', '(.*)'", html_content).group(1)
        if currency_flag not in self.currency_cache:
            pubUtil.send_email('new Currency from MM!', currency_flag)
        currency = self.currency_cache.get(currency_flag, 'CNY')
        for flights in flight_data:
            flightNumber = flights.get('flightNumber')
            depTime = flights.get("departureTime")
            depTime = time.mktime(time.strptime(depTime,'%Y/%m/%d %H:%M:%S'))
            arrTime = flights.get("arrivalTime")
            arrTime = time.mktime(time.strptime(arrTime,'%Y/%m/%d %H:%M:%S'))
            depAirport = flights.get("originCode")
            arrAirport = flights.get("destinationCode")
            adultTax = float(flights.get("taxAdult"))
            carrier = flightNumber[0:2]
            # isChange = flights.get("arrivalTime")
            # segments = flights.get("arrivalTime")
            getTime = time.time
            # fromCity = flights.get("origin")
            # toCity = flights.get("destination")
            fares = flights.get("fares")
            detail_message = fares.get("happy")
            if not detail_message:
                detail_message = fares.get('happlus')
                if not detail_message:
                    detail_message = fares.get("prime")
            netFare = detail_message.get("fare")
            maxSeats = detail_message.get("seat")
            cabin = detail_message.get("bookingClass")
            adultPrice = netFare + adultTax  

            item = LmdSpidersItem()
            item.update(dict(
                flightNumber=flightNumber,
                depAirport=depAirport,
                arrAirport=arrAirport,
                carrier=carrier,
                depTime=depTime,
                arrTime=arrTime,
                currency=currency,
                # segments=json.dumps([segment]),
                isChange=1,
                getTime=time.time(),
                fromCity=self.portCitys.get(depAirport, depAirport),
                toCity=self.portCitys.get(arrAirport, arrAirport),
                adultPrice=adultPrice,
                netFare=netFare,
                maxSeats=maxSeats,
                adultTax=adultTax,
                cabin=cabin,
            ))
            yield item