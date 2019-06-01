# -*- coding: utf-8 -*-
import re
import json
import time
try:
    from urllib import parse
except:
    import urllib as parse
from datetime import datetime, timedelta

import scrapy

from utils import dataUtil, pubUtil
from utils.spe_util import vyUtil
from lmd_spiders.items import LmdSpidersItem


class V7Spider(scrapy.Spider):
    name = 'v7'
    allowed_domains = ['booking.volotea.com']
    start_urls = ['https://booking.volotea.com/Search.aspx?',
                  'https://booking.volotea.com/FindFlightAjax.aspx']
    carrier = 'V7'
    task = []
    version = 1.2
    isOK = True
    currency_cache = {
        u'€': u'EUR',
        u'£': u'GBP',
        u'$': u'USD',
    }

    custom_settings = dict(
        GET_SESSION_PARAMS={
            'culture': 'en-GB',
            'bookingtype': 'flight',
            # 'from': 'VCE',
            # 'to': 'JSI',
            # 'departuredate': '2018-08-15',
            'currency': 'EUR',
            # 'returnDate': '',
            'adults': 5,
            'children': 0,
            'infants': 0,
            'showNewSearch': False,
            'triptype': 'OneWay',
            # 'residentFamilyType': '',
            'useCookie': False,
        },
        PROXY_TRY_NUM=5,
        DOWNLOAD_TIMEOUT=30,

        DEFAULT_REQUEST_HEADERS={
            'Host': "booking.volotea.com",
            'Connection': "keep-alive",
            'Cache-Control': "no-cache",
            'Origin': "https://booking.volotea.com",
            'Upgrade-insecure-requests': "1",
            'Content-Type': "application/x-www-form-urlencoded",
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
            'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "zh-CN,zh;q=0.9",
        },

        # LOG_LEVEL = 'DEBUG',

        POST_HEADERS={
            'Host': 'booking.volotea.com',
            'Origin': 'https://booking.volotea.com',
            'Referer': 'https://booking.volotea.com/CalendarSelect.aspx?culture=en-GB',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
            'Accept': 'text/html, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        

        RETRY_ENABLED=False,

        CONCURRENT_REQUESTS=8,

        DOWNLOADER_MIDDLEWARES={
             'lmd_spiders.middlewares.StatisticsItem': 200,
             'lmd_spiders.middlewares.V7ProxyMiddleware': 300,
        },

        COOKIES_ENABLED=True,

        # ITEM_PIPELINES={ # 往测试库添加数据
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()
        self.dt_to_ts = lambda x: time.mktime(time.strptime(x, '%m/%d/%Y %H:%M'))

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl(self.name, 1)
            if not result:
                self.log('get task error'), 20
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to, days) = vyUtil.analysisData(data)  # 把获取到的data格式化
                # dep, to, dt, days= 'RHO', 'PMO', '2018-08-15', 30
                dt_datetime = datetime.strptime(dt, '%Y%m%d')
                end_date = dt_datetime + timedelta(days=int(days))
                dt = dt_datetime.strftime('%Y-%m-%d')

                if dt_datetime.month != end_date.month:
                    next_fday = datetime(end_date.year, end_date.month, 1)
                    days_before = (next_fday - dt_datetime).days
                    next_fday_str = next_fday.strftime('%Y-%m-%d')
                    yield self.first_request(dep, to, dt, days_before + 1)
                    yield self.first_request(dep, to, next_fday_str, int(days) - days_before)
                else:
                    yield self.first_request(dep, to, dt, days)
                    
    def first_request(self, dep, to, dt, days):
        params = {
            'from': dep,
            'to': to,
            'departuredate': dt,
        }
        params.update(self.custom_settings.get('GET_SESSION_PARAMS'))
        # total_url = self.start_urls[0] + urllib.urlencode(params)
        total_url = self.start_urls[0] + parse.urlencode(params)
        meta = {
            'from': dep,
            'to': to,
            'departuredate': dt,
            'days': days
        }
        return scrapy.Request(
                                url=total_url,
                                meta=meta,
                                headers=self.custom_settings.get('POST_HEADERS'),
                                dont_filter=True,
                                callback=self.date_parse,
                                errback=self.errback,
                                )

    def errback(self, failure):
        self.log(failure.value, 40)
        self.log(failure.request.meta.get('proxy'), 40)
        self.isOK = False
        # time.sleep(8)
        return failure.request
    
    def date_parse(self, response):
        self.isOK = True
        # self.log('date is parse...', 20)
        cookies = response.request.headers.getlist('Cookie')[0]
        headers = {'Cookies': cookies}
        headers.update(self.custom_settings.get('POST_HEADERS'))
        dates = response.xpath('//div[@id="element-data"]/a/@data-dept-date').extract()
        dep_date = datetime.strptime(response.meta.get('departuredate'), '%Y-%m-%d')
        days = response.meta.get('days')
        dep = response.meta.get('from')
        to = response.meta.get('to')
        # print(dates)
        for date in dates:
            dts = re.match(r'(\d{4}-\d{2}-\d{2})',  date)
            if not dts:
                continue
            dt = dts.group()
            dt_datetime = datetime.strptime(dt, '%Y-%m-%d')
            diff_day = (dt_datetime - dep_date).days
            if diff_day < 0 or diff_day > days:
                continue
            data_post = dict(
                date=dt,
                market='1',
                origin=dep,
                destination=to
            )
            yield scrapy.FormRequest(
                                    url=self.start_urls[1],
                                    formdata=data_post,
                                    # meta={'data': data_post},
                                    headers=headers,
                                    dont_filter=True,
                                    callback=self.parse,
                                    errback=self.errback,
                                    )

    def parse(self, response):
        self.isOK = True
        self.log('data is parseing.....', 20)
        # print(response.meta.get('data'))
        # print(response.body)
        _as = response.xpath('//div/a')
        for a in _as:
            try:
                flag = a.xpath('./@data-is-super').extract()[0]
            except:
                continue
            if flag == 'true':
                continue
            
            jour_key = a.xpath('./@data-journeykey').extract()[0]
            s = filter((lambda x: x), re.split(r'[~|\s]+', jour_key))
            carrier, number, dep, dep_date, dep_time, arr, arr_date, arr_time = s
            flightNumber = carrier + number
            dep_ts = self.dt_to_ts('%s %s' % (dep_date, dep_time))
            arr_ts = self.dt_to_ts('%s %s' % (arr_date, arr_time))

            seats_str = a.xpath('./@data-free-places').extract()
            try:
                seats = int(seats_str[0])
            except:
                seats = 9
            jour_fare = a.xpath('./@data-journeyfare').extract()[0]
            fare_dict = json.loads(jour_fare)[0]
            tax = fare_dict.get('tax')
            netFare = fare_dict.get('farePrice')
            price_str = a.xpath('./@data-price-format').extract()[0]
            currency = self.currency_cache.get(price_str[0], 'EUR')
            price = float(price_str[1:])

            fare_key = a.xpath('./@data-farekey').extract()[0]
            s_f = filter((lambda x: x), re.split(r'[~|\s]+', fare_key))
            cabin = s_f[3]

            seg_dep = a.xpath('./@data-dept-date').extract()[0] + ':00'
            seg_arr = a.xpath('./@data-date').extract()[0] + ':00'
            segment = dict(
                flightNumber=flightNumber,
                aircraftType='',
                number=1,
                airline=carrier,
                dep=dep,
                dest=arr,
                departureTime=seg_dep,
                destinationTime=seg_arr,
                depTerminal='',
                seats=seats,
                duration=dataUtil.gen_duration(dep_ts, arr_ts),
            )
            
            item = LmdSpidersItem()
            item.update(dict(
                flightNumber=flightNumber,
                depAirport=dep,
                arrAirport=arr,
                carrier=carrier,
                depTime=dep_ts,
                arrTime=arr_ts,
                currency=currency,
                segments=json.dumps([]),
                isChange=1,
                getTime=time.time(),
                fromCity=self.portCitys.get(dep, dep),
                toCity=self.portCitys.get(arr, arr),
                cabin=cabin,
                adultPrice=price,
                netFare=netFare,
                adultTax=tax,
                maxSeats=seats,
            ))
            # print item
            yield item

