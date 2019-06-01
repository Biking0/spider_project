# -*- coding: utf-8 -*-
import scrapy,re,time,json,logging,os,csv,random,traceback
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta
from utils import dataUtil
from utils import pubUtil


class DpSpider(scrapy.Spider):
    name = 'dp'
    allowed_domains = ['pobeda.aero']
    start_urls = ['https://booking.pobeda.aero/ExternalSearch.aspx']
    version = 1.2
    task = []
    isOK = True
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 200,
            # 'wow_spider.middlewares.XQSessionMiddleware': 300,
        },
        AJAX_URL ='https://booking.pobeda.aero/AjaxTripAvailaibility.aspx',
        DOWNLOAD_TIMEOUT=20,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=8,
        COOKIES_ENABLED=True,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=8,
        SEAT=5,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS={
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'referer': "https://booking.pobeda.aero/Search.aspx",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            # 'cookie': "_ga=GA1.2.1566014824.1537856783; _gid=GA1.2.295716253.1537856783; ASP.NET_SessionId=clvqakq5vfio21jvz3u5bk1k; CultureCode=%7b%22Value%22%3a%22ru-RU%22%7d; skysales=!KRtGE8HJicvuQDk8ac0SZ4cwGUzSozWDWMBE5msg1FajAdK1hXGqq38XCDGe4kz3SRQ1TWTHdEBV1DE=; _ym_uid=1537856788764532536; _ym_d=1537856788; _ym_isad=2; PassengersInfoCookie=%7b%22Value%22%3a%22%22%7d; ContactInfoCookie=%7b%22Value%22%3a%22%22%7d; rxVisitor=1537857632647SCAFNUB0F8OOQP8RPV1RT3MC15HJM32B; _ga=GA1.3.1566014824.1537856783; _gid=GA1.3.295716253.1537856783; _ctuid=0f8411bf-69ff-45e2-a5c8-e928ee67ad24; __ssid=259aadc3fd82e123bbab0228efeb789; _ym_uid=1537856788764532536; _ym_d=1537856788; _ym_isad=2; rxVisitor=1537857632647SCAFNUB0F8OOQP8RPV1RT3MC15HJM32B; _ctuid=0f8411bf-69ff-45e2-a5c8-e928ee67ad24; __ssid=259aadc3fd82e123bbab0228efeb789; _gat=1; _gat_UA-56206873-1=1; ; adsas=; _ga=GA1.3.1566014824.1537856783; _gid=GA1.3.295716253.1537856783; sessionControl=%7B%22ownership%22%3A%7B%22sessionOwnerId%22%3A%227cf6907c-6d69-632c-59ac-9ebe875d6e5d%22%2C%22sessionOwnerPage%22%3A%22https%3A%2F%2Fbooking.pobeda.aero%2FScheduleSelect.aspx%22%2C%22lastUpdated%22%3A1537870387159%7D%7D; userSearchConfiguration=%7B%22From%22%3A%22VKO%22%2C%22InboundDate%22%3A%222018-11-10%22%2C%22To%22%3A%22BGY%22%2C%22OutboundDate%22%3A%222018-10-10%22%2C%22MinADT%22%3A0%2C%22MinCHD%22%3A0%2C%22MinINFT%22%3A0%2C%22SelectedADT%22%3A%224%22%2C%22MaxPax%22%3A0%2C%22TripType%22%3Atrue%2C%22LinkBooking%22%3Anull%2C%22MinDepartureDate%22%3Anull%2C%22MaxDepartureDate%22%3Anull%2C%22MinArrivalDate%22%3Anull%2C%22MaxArrivalDate%22%3Anull%2C%22Culture%22%3A%22en%22%2C%22CurrencyCode%22%3A%22USD%22%2C%22FlexibleDates%22%3Afalse%2C%22Success%22%3Atrue%2C%22AnyFieldWithData%22%3Afalse%7D; dtSa=true%7CC%7C-1%7CFIND%20FLIGHTS%7C-%7C1537870405110%7C70388824_77%7Chttps%3A%2F%2Fbooking.pobeda.aero%2FSearch.aspx%7CPobeda%7C1537870398994%7C; sessionControl=%7B%22ownership%22%3A%7B%22sessionOwnerId%22%3A%227cf6907c-6d69-632c-59ac-9ebe875d6e5d%22%2C%22sessionOwnerPage%22%3A%22https%3A%2F%2Fbooking.pobeda.aero%2FScheduleSelect.aspx%22%2C%22lastUpdated%22%3A1537871372315%7D%7D; tmr_detect=0%7C1537871380122; dtPC=1$71374245_64h-vEPGHUMKOBBJMFPANJKPODVLSICPPOLOD; dtLatC=2; rxvt=1537873182432|1537866687914; userSearchConfiguration=%7B%22From%22%3A%22VKO%22%2C%22InboundDate%22%3A%222018-11-10%22%2C%22To%22%3A%22BGY%22%2C%22OutboundDate%22%3A%222018-11-04%22%2C%22MinADT%22%3A0%2C%22MinCHD%22%3A0%2C%22MinINFT%22%3A0%2C%22SelectedADT%22%3A%224%22%2C%22MaxPax%22%3A0%2C%22TripType%22%3Atrue%2C%22LinkBooking%22%3Anull%2C%22MinDepartureDate%22%3Anull%2C%22MaxDepartureDate%22%3Anull%2C%22MinArrivalDate%22%3Anull%2C%22MaxArrivalDate%22%3Anull%2C%22Culture%22%3A%22en%22%2C%22CurrencyCode%22%3A%22USD%22%2C%22FlexibleDates%22%3Afalse%2C%22Success%22%3Atrue%2C%22AnyFieldWithData%22%3Afalse%7D; dtCookie=1$5B50DBD8960E6F5FF2A85EDCA1FBED65|RUM+Default+Application|1; dtSa=true%7CC%7C-1%7CFIND%20FLIGHTS%7C-%7C1537871388510%7C71374245_64%7Chttps%3A%2F%2Fbooking.pobeda.aero%2FSearch.aspx%7CPobeda%7C1537871382433%7C",
            # 'cookie':'ASP.NET_SessionId=clvqakq5vfio21jvz3u5bk1k; ',
            'cookie':'ASP.NET_SessionId=vmpdxiqkz4fsp23qzlp5msot; ',
        },
        AJAX_HEADERS ={
            'accept': "*/*",
            'origin': "https://booking.pobeda.aero",
            'x-requested-with': "XMLHttpRequest",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            'content-type': "application/x-www-form-urlencoded",
            'referer': "https://booking.pobeda.aero/ScheduleSelect.aspx",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cookie':'ASP.NET_SessionId=vmpdxiqkz4fsp23qzlp5msot; ',
        },
        CURRENCY_CACHE={
            u'$': u'USD',  # 美元
            u'руб.': u'RUB',  # 卢布
            # u'THB': u'THB',
            # u'HK$': u'HKD',  # 港币
            # u'NT$': u'TWD',  # 台币
            # u'CNY': u'CNY',
        },
    )





    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()



    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name,self.name,self.num,permins,self.version))
        result_iter = None
        result = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter or not result:
                    result_iter = self.get_task()
                result = next(result_iter)
                print result[0]
            else:
                result = pubUtil.getUrl('DP', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to,days) = pubUtil.analysisData_5j(data)
            # for i in range(1):
            # for data in self.get_task():
            #     dep, to, dt = data
                # dt,dep,to= '2018-10-16','VKO','KJA'
                for i in range(-1,int(days)):
                    if i == -1:
                        # print(dep, to, dt)
                        seat = self.custom_settings.get('SEAT')
                        querystring = {
                            "marketType": "OneWay",
                            "fromStation": dep,
                            "toStation": to,
                            "beginDate": "04-11-2018",
                            # "endDate": "10-11-2018",
                            "adultCount": seat,
                            "currencyCode": "USD",
                            "utm_source": "pobeda",
                            "culture": "en-US"
                        }
                        url = self.start_urls[0] + '?'
                        for key in querystring:
                            url = url + key + '=' + str(querystring.get(key)) + '&'

                        invalid = {
                            'date': dt.replace('-', ''),
                            'depAirport': dep,
                            'arrAirport': to,
                            'mins': self.custom_settings.get('INVALID_TIME')
                        }
                        meta_data = dict(
                            invalid=invalid,
                            params=querystring,
                            aaa=(dep, to, dt),
                            flight_time=dt
                        )
                        yield scrapy.Request(url,
                                             callback=self.parse,
                                             method='GET',
                                             headers=self.custom_settings.get('HEADERS'),
                                             meta={'meta_data': meta_data},
                                             errback=self.errback
                                             )
                        continue
                    dep_tupletime = datetime.strptime(dt, '%Y-%m-%d')
                    date = dep_tupletime + timedelta(days=i)
                    dt_get = date.strftime('%Y-%m-%d')
                    print(dep, to, dt_get)
                    raw = 'indexTrip=1&dateSelected=%s&isChangeFlightFlow=false'%dt_get
                    invalid = {
                        'date': dt_get.replace('-', ''),
                        'depAirport': dep,
                        'arrAirport': to,
                        'mins': self.custom_settings.get('INVALID_TIME')
                    }
                    meta_data = dict(
                        invalid=invalid,
                        raw=raw,
                        aaa=(dep, to, dt),
                        flight_time=dt
                    )
                    yield scrapy.Request(self.custom_settings.get('AJAX_URL'),
                                         callback=self.parse,
                                         method='POST',
                                         body=raw,
                                         headers=self.custom_settings.get('AJAX_HEADERS'),
                                         meta={'meta_data': meta_data},
                                         errback=self.errback
                                         )



    def parse(self, response):
        self.isOK = True
        if response.xpath('//*[@id="selectMainBody"]/h2'):
            print(response.xpath('//*[@id="selectMainBody"]/h2').extract()[0])
            return
        # print(response.xpath('//*[@id="market1"]/td[2]/div/span').extract()[0])
        flights = response.xpath('//tr[@id="market1"]')

        for flight in flights:
            # 当天没有航班
            if not flight.xpath('./@data-ismacjourney'):
                print('No flight to day')
                return
            #判断是否中转
            change = flight.xpath('//td[@class="direction JourneyInfo"]/div').extract()
            if len(change) > 2:
                # print('is change')
                continue
            flightNumber = flight.xpath('.//div[@class="code"]/text()').extract()[0]
            carrier = re.compile('\D+').search(flightNumber).group()

            dep_dt_str = flight.xpath('./@data-departuretime').extract()[0]
            dep_tupletime = time.strptime(dep_dt_str, '%Y-%m-%dT%H:%M:00')
            depTime = time.mktime(dep_tupletime)
            # 判断第二天的情况
            arr_dt_str = flight.xpath('./@data-arrivaltime').extract()[0]
            arr_tupletime = time.strptime(arr_dt_str, '%Y-%m-%dT%H:%M:00')
            arrTime = time.mktime(arr_tupletime)
            depAirport = flight.xpath('./@data-departure-code').extract()[0]
            arrAirport = flight.xpath('./@data-arrival-code').extract()[0]
            isChange = 1
            price = flight.xpath('.//span[@style="font-size: 12"]/text()').extract()[0].split('  ')
            info = flight.xpath('.//input/@value').extract()[0]
            adultPrice = float(price[0].replace(' ', '').replace(',', '.'))
            adultTax = 0
            netFare = adultPrice - adultTax
            currency_unit = price[1]
            currency = self.custom_settings.get('CURRENCY_CACHE').get(currency_unit, currency_unit)
            # 目前暂未发现座位,使用请求的座位
            maxSeats = self.custom_settings.get('SEAT')

            cabin = 'X'

            # segments = dict(
            #     flightNumber=flightNumber,
            #     aircraftType=aircraftType,
            #     number=1,
            #     departureTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(depTime)),
            #     destinationTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(arrTime)),
            #     airline=carrier,
            #     dep=depAirport,
            #     dest=arrAirport,
            #     seats=maxSeats,
            #     duration=duration,
            #     depTerminal=''
            # )
            getTime = time.time()

            item = WowSpiderItem()
            item['flightNumber'] = flightNumber
            item['depTime'] = depTime
            item['arrTime'] = arrTime
            item['fromCity'] = self.portCitys.get(depAirport, depAirport)
            item['toCity'] = self.portCitys.get(arrAirport, arrAirport)
            item['depAirport'] = depAirport
            item['arrAirport'] = arrAirport
            item['currency'] = currency
            item['adultPrice'] = adultPrice
            item['adultTax'] = adultTax
            item['netFare'] = netFare
            item['maxSeats'] = maxSeats
            item['cabin'] = cabin
            item['carrier'] = carrier
            item['isChange'] = isChange
            item['segments'] = '[]'
            item['getTime'] = getTime
            item['info'] = info
            yield item
            # print(item)


    def get_task(self):
        print "local task"
        inputFile = open(os.path.join('utils', 'DP.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 30
        add_num = random.randint(1,20)
        for i in range(add_num, 30, days):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y%m%d')
            for data in datas:
                if not data or not len(data):
                    continue
                # yield (data[0], data[1], _dt)
                yield ['%s-%s:%s:%s' % (data[0], data[1], _dt, days)]
                # task = [('VKO','BGY','2018-10-06'),('BGY','LED','2018-10-06'),('VKO','PSA','2018-10-06')]
                # for i in task:
                #     yield i


    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-' * 40)
        print(failure.value)
        yield failure.request

