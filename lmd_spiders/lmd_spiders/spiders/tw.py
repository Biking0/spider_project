# -*- coding: utf-8 -*-
import scrapy, logging, time, json, traceback
from utils import dataUtil, pubUtil
from lmd_spiders import settings
from datetime import datetime, timedelta
from lmd_spiders.items import LmdSpidersItem
from utils.spe_util import twUtil
import urllib


class TwSpider(scrapy.Spider):
    name = 'tw'
    allowed_domains = ['twayair.com']
    start_urls = ['https://www.twayair.com/booking/ajax/setBookingParam.do?',
                  'https://www.twayair.com/booking/ajax/searchAvailability.do?']
    search_id = None
    carrier = 'TW'
    task = []
    version = 1.1

    custom_settings = dict(
        COOKIE_HEADERS={
            'Host': 'www.twayair.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.twayair.com/main.do?_langCode=EN',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/66.0.3359.181 Safari/537.36',
        },

        GET_COOKIES_URL='https://www.twayair.com/booking/availabilityList.do',

        COOKIES_ENABLED=True,

        CONCURRENT_REQUESTS=1,

        DOWNLOADER_MIDDLEWARES={
            'lmd_spiders.middlewares.TWCookieMiddleware': 300,
            'lmd_spiders.middlewares.StatisticsItem': 200,
        },

        DEFAULT_REQUEST_HEADERS={
            'Host': 'www.twayair.com',
            'Connection': 'keep-alive',
            'Accept': 'txt/html, */*; q=0.01',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, '
                          'like Gecko) Mobile/14G60',
            'Referer': 'https://www.twayair.com/booking/availabilityList.do',
            'Accept-Encoding': 'gzip',
            'Accept-Language': 'zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'X-Requested-With': 'XMLHttpRequest',
        },

        # LOG_LEVEL="DEBUG",

        # ITEM_PIPELINES={
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        super(TwSpider, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        result_iter = None
        while True:

            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pubUtil.get_task(self.name, days=30)
                result = next(result_iter)
            else:
                result = pubUtil.getUrl('TW', 5)

            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            today = datetime.now().strftime('%Y%m%d')
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)  # 把获取到的data格式化
                # dt, dep, to = '20180722', 'ICN', 'KIX' # 测试某条数据
                params = urllib.urlencode(dict(
                    origin=dep,
                    destination=to,
                    onwardDateStr=dt.replace('-', ''),
                    # pointOfPurchase='KR',
                    paxTypeCountStr='3,0,0',
                    today=today,
                    travelType='OW',
                    searchType='byDate',
                    # domesticYn='Y',
                    bundleAmountOW=0,
                    bundleAmountRT=0,
                    routeCls='AS',
                    _=int(time.time() * 1000)
                ))
                total_url = self.start_urls[0] + params
                yield scrapy.Request(url=total_url,
                                     callback=self.transit,
                                     meta={'params': params, 'flag': 1},
                                     dont_filter=True)

    def transit(self, response):
        params = response.meta.get('params')
        total_url = self.start_urls[1] + params
        yield scrapy.Request(url=total_url,
                             meta={'params': params},
                             dont_filter=True, )

    def parse(self, response):
        if 'Enter the captcha code' in response.body:  # 被封IP, 需要输入验证码， 嗯。。。就算输正确也是让你继续输的那种
            time.sleep(2)
            self.log('please input captcha code', 20)
            params = response.meta.get('params')
            total_url = self.start_urls[0] + params
            yield scrapy.Request(url=total_url,
                                 callback=self.transit,
                                 meta={'params': params, 'flag': 1},
                                 dont_filter=True)
            return

        trs = response.xpath('//tbody[@id="tbodyOnward"]/tr[not(@class)]')
        for tr in trs:

            td_px = tr.xpath('td[contains(@class, "px")]')
            if not int(len(td_px)):
                continue
            td_0 = td_px[0]
            ischange = int(td_0.xpath('input[@name="stops"]/@value').extract_first())
            if ischange:
                continue

            duration = twUtil.format_duration(tr.xpath('td/span[@class="f_time"]/text()').extract_first())
            flightNumber = td_0.xpath('input[@name="flightNumber"]/@value').extract_first()
            airline = td_0.xpath('input[@name="carrierCode"]/@value').extract_first()
            depTime = twUtil.format_time(td_0.xpath('input[@name="scheduledDepartureDateTime"]/@value').extract_first())
            arrTime = twUtil.format_time(td_0.xpath('input[@name="scheduledArrivalTime"]/@value').extract_first())
            dep = td_0.xpath('input[@name="origin"]/@value').extract_first()
            dest = td_0.xpath('input[@name="destination"]/@value').extract_first()
            carrier = td_0.xpath('input[@name="airlineCode"]/@value').extract_first()
            dep_seg = dataUtil.format_seg_time(depTime)
            dest_seg = dataUtil.format_seg_time(arrTime)

            seats, fare, tax, cabin, currency = 0, 0, 0, None, None  # 数据初始化

            for td in td_px:  # 获取最低价
                try:
                    span = td.xpath('label/span')
                    if not len(span):
                        continue
                except:  # 当前舱位无票
                    traceback.print_exc()
                    continue
                fare = span.xpath('input[@name="fare"]/@value').extract_first()
                seats = span.xpath('input[@name="numberOfSeats"]/@value').extract_first()
                tax_part = span.xpath('input[@name="tax"]/@value').extract_first()
                surcharge = span.xpath('input[@name="surcharge"]/@value').extract_first()
                cabin = span.xpath('input[@name="fareClass"]/@value').extract_first()
                currency = span.xpath('input[@name="currency"]/@value').extract_first()
                tax = float(tax_part) + float(surcharge)
                if int(seats) >= 3:
                    break

            seg = {'flightNumber': flightNumber}
            seg['aircraftType'] = ''
            seg['number'] = 1
            seg['airline'] = airline
            seg['dep'] = dep
            seg['dest'] = dest
            seg['duration'] = duration
            seg['departureTime'] = dep_seg
            seg['destinationTime'] = dest_seg
            seg['depTerminal'] = ''
            seg['seats'] = seats

            item = LmdSpidersItem()
            item['maxSeats'] = seats
            item['flightNumber'] = flightNumber
            item['depTime'] = depTime
            item['arrTime'] = arrTime
            item['depAirport'] = dep
            item['arrAirport'] = dest
            item['cabin'] = cabin
            item['currency'] = currency
            item['carrier'] = carrier
            item['isChange'] = 1
            item['getTime'] = time.time()
            item['adultPrice'] = float(fare) + tax
            item['adultTax'] = tax
            item['netFare'] = fare
            item['fromCity'] = self.portCitys.get(dep, dep)
            item['toCity'] = self.portCitys.get(dest, dest)
            item['segments'] = '[]'
            yield item
