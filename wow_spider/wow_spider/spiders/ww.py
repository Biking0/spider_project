# -*- coding: utf-8 -*-
import scrapy,json
import time,urllib,logging
from wow_spider.items import WowSpiderItem
from jsonpath import jsonpath
from datetime import datetime
from utils import dataUtil
from utils import pubUtil


class WwSpider(scrapy.Spider):
    name = 'ww'
    allowed_domains = ['wowair.co.uk']
    # start_urls = ['https://booking.wowair.com/api/midgardurCore/v5/bundles?ApiKey=&Adults=1&Infants=0&Children=0&PromoCode=&Currency=GBP&Flights[0].origin=AMS&Flights[0].destination=KEF&Flights[0].departureDate=2018-08-03']
    start_urls = ['https://booking.wowair.com/api/midgardurCore/v5/bundles?']
    carrier = 'WW'
    version = 1.4
    task = []
    isOK = True
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            # 'lamudatech_dev.middlewares.LamudatechDevDownloaderMiddleware': 543,
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 300,

        },
        DOWNLOAD_TIMEOUT=20,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM = 8,
        COOKIES_ENABLED=False,
        INVALID_TIME = 45,

        RETRY_ENABLED = False,

        # ITEM_PIPELINES = {
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # }


    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()


    def start_requests(self):
        permins =0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl('WW', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt,dep,to) = pubUtil.analysisData(data)

                # dt, dep, to = '2018-08-03', 'AMS', 'KEF'
                temp = {
                    'ApiKey' : '',
                    'Adults' : '3',
                    'Infants': '0',
                    'Children': '0',
                    'PromoCode':'',
                    'Currency': 'USD',
                    'Flights[0].origin':dep,
                    'Flights[0].destination':to,
                    'Flights[0].departureDate':dt,
                }
                invalid = {
                    'date' : dt.replace('-',''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins':self.custom_settings.get('INVALID_TIME')
                }
                url =  '%s%s'%(self.start_urls[0],urllib.urlencode(temp))
                yield scrapy.Request(url, 
                                    callback=self.parse,
                                    dont_filter=True,
                                    meta={'invalid':invalid},
                                    errback=self.errback)
                # break
    
    def errback(self, failure):
        self.log(failure.value, 40)
        self.isOK = False
        return failure.request




    def parse(self,response):
        self.isOK = True
        # print(response.status)
        if len(response.body) == 0 or response.status == 502:
            self.task.append(response.meta.get('invalid'))
            return
        # print(response)
        json_dict = json.loads(response.body)
        for data in json_dict:
            item = WowSpiderItem()
            if len(data.get('legDetails')) > 1:continue #判断是否中转
            flightNumber = data.get('carrierCode') + data.get('flightNumber')
            depTime = time.strptime(data.get('departureTime'),'%Y-%m-%dT%H:%M:%S')
            depAirport = data.get('origin')
            arrAirport = data.get('destination')
            arrTime = time.strptime(data.get('arrivalTime'), '%Y-%m-%dT%H:%M:%S')
            arrline = data.get('carrierCode')
            duration = data.get('flightTime')
            item["flightNumber"] = flightNumber
            item['depTime'] = time.mktime(depTime)
            item['arrTime'] = time.mktime(arrTime)
            item['depAirport'] = depAirport
            item['arrAirport'] = arrAirport
            item['fromCity'] = self.portCitys.get(depAirport, depAirport)
            item['toCity'] = self.portCitys.get(arrAirport,arrAirport)

            #判断是否有票/
            available = data.get('bundles')
            if available.get('BUNB').get('available'):
                price_all = available.get("BUNB")
            elif available.get('BUND').get('available') :
                price_all = available.get("BUND")
            elif available.get('BUNC').get('available'):
                price_all = available.get("BUNC")
            elif available.get('BUNZ').get('available'):
                price_all = available.get("BUNZ")
            else:
                continue
            # price_all = available.get("BUNB")
            item['currency'] = jsonpath(price_all,'$..currency')[0]
            item['adultPrice'] = jsonpath(price_all,'$..fareWithTaxes')[0]
            item['netFare'] = jsonpath(price_all,'$..fareWithoutTaxes')[0]
            item['cabin'] = jsonpath(price_all,'$..fareClassCode')[0]
            item['adultTax'] = jsonpath(price_all,'$..fareWithTaxes')[0] - jsonpath(price_all,'$..fareWithoutTaxes')[0]
            item["carrier"] = arrline
            item["maxSeats"] = jsonpath(price_all,'$..seatsAvailable')[0]
            segments = dict(
                flightNumber=flightNumber,
                aircraftType=data.get('aircraftType').replace(' ','-'),
                number=1,
                departureTime=time.strftime('%Y-%m-%d %H:%M:%S',depTime),
                destinationTime=time.strftime('%Y-%m-%d %H:%M:%S',arrTime),
                airline=arrline,
                dep=depAirport,
                dest=arrAirport,
                seats=jsonpath(price_all,'$..seatsAvailable')[0],
                duration='%02d:%02d'%(duration/60,duration%60),
                depTerminal=''
            )
            item['segments'] = '[]'
            item['getTime'] = time.time()
            yield item
            # print('-----------------------------')
            # print(item)

