# -*- coding: utf-8 -*-
import scrapy,re,time,json,logging,os,csv,random,traceback
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta
from utils import dataUtil
from utils import pubUtil


class BjSpider(scrapy.Spider):
    name = 'bj'
    allowed_domains = ['nouvelair.com']
    start_urls = ['http://api-mobile.nouvelair.com/api/recherche/en/']
    version = 1.2
    task = []
    isOK = True
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            # 'wow_spider.middlewares.ProxyMiddleware': 200,
            # 'wow_spider.middlewares.BJCookieMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=20,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=3,
        # COOKIES_ENABLED=True,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=10,
        SEAT=3,
        DURATION=7,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS={
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-cn',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'DeviceId': 'F61B0ADF-4EB5-45A3-B8C3-4EAA555AF219',
            'Pragma': 'no-cache',
            'User-Agent': 'nouvelair/1.0.9 CFNetwork/811.5.4 Darwin/16.7.0'
        },

        #设置100是找不到有票的航班DUSMIR
        OTHERFEE={
            'CDGMIR':11,"TLSTUN":2,"TUNCDG":11,
            "MIRDUS":11,"STRMIR":11,"DUSDJE":100,
            "DJEHAD":100,"LEJMIR":11,"DJEDUS":100,
            "STRDJE":100,"DUSMIR":11,"CDGTUN":11,
            "MIRLEJ":11,"MIRCDG":11,"MIRNCE":11,
            "MIRDJE":100,"MIRHAJ":11,"MIRTXL":11,
            "MIRTUN":100,"MIRSTR":11,"TUNNCE":11,
            "TUNLYS":11,"TUNMIR":100,"CDGDJE":11,
            "TUNTLS":11,"DJEMIR":100,"MIRMUC":11,
            "DJEHAJ":100,"DJELYS":11,"LYSMIR":11,
            "MIRNTE":100,"HAJMIR":11,"TUNMRS":11,
            "NCETUN":11,"DJECDG":11,"NTEDJE":11,
            "DJELEJ":100,"DJEMUC":11,"TUNALG":12,
            "LYSTUN":11,"MRSTUN":11,"DJESTR":100,
            "NTETUN":11,"TXLMIR":11,"DJETXL":100,
            "ALGTUN":94,"DJENTE":11,"LYSDJE":11,
            "TUNNTE":11,"MUCMIR":11,
        }
    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl('BJ', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to, days) = pubUtil.analysisData_5j(data)
            # for i in range(1):
            # for data in self.get_task():
            #     dep, to, dt = data
            #     dt,dep,to= '2018-11-16','TUN','MRS'
                print(dep, to, dt)
                seat = self.custom_settings.get('SEAT')
                duration = self.custom_settings.get("DURATION")
                # self.log('%s:%s:%s:%s' % (dt, dep, to, days), 20)
                for i in range(0, int(days), duration):
                    begin_dt, end_dt = pubUtil.time_add_5j(dt, i, duration)
                    payload = {
                        'adultes': seat,
                        'aller': begin_dt,
                        'bebes': '0',
                        'devise': 'TND',
                        'enfants': '0',
                        'felxibilite': '3',
                        'retour': '',
                        'sens': '1'
                    }
                    body = ''
                    for key in payload:
                        body = body + key  + '=' + str(payload.get(key)) + '&'
                    url = self.start_urls[0] + '%s/%s'%(dep,to)
                    invalid = {
                        'date': dt.replace('-', ''),
                        'depAirport': dep,
                        'arrAirport': to,
                        'mins': self.custom_settings.get('INVALID_TIME'),
                    }
                    meta_data = dict(
                        invalid=invalid,
                        payload=body,
                        aaa=(dep, to, dt),
                        url=url,
                    )
                    yield scrapy.Request(url,
                                         callback=self.parse,
                                         method='POST',
                                         headers=self.custom_settings.get('HEADERS'),
                                         meta={'meta_data': meta_data},
                                         body=body,
                                         errback=self.errback
                                         )

    def parse(self, response):
        # print(response.text)
        # self.isOK = True
        # print len(response.text)
        if len(response.text) == 0:
            print "not flight"
            return
        data_dict = json.loads(response.text)
        #特殊的结果
        days_data = data_dict.get('AirAvailabilityData')
        if type(days_data) == dict:
            days_data = [data_dict.get('AirAvailabilityData').get('1')]

        for day_data in days_data:
            #判断中转
            flight = day_data.get('flight')

            if len(flight) > 1:
                print "is change"
                continue

            flight_segment = flight[0]
            carrier = flight_segment.get('Carrier')
            flightNumber = carrier + flight_segment.get('Flight')
            deptime_tuple = time.strptime(flight_segment.get('Depart'), '%Y-%m-%dT%H:%M:00')
            depTime = time.mktime(deptime_tuple)
            arrtime_tuple = time.strptime(flight_segment.get('Arrivee'), '%Y-%m-%dT%H:%M:00')
            arrTime = time.mktime(arrtime_tuple)
            depAirport = flight_segment.get('From')
            arrAirport = flight_segment.get('To')
            maxSeats = int(flight_segment.get('Stock'))

            adultPrice = day_data.get('prix') / self.custom_settings.get("SEAT") - 76
            currency = day_data.get('deviseGet')




            adultTax = 0
            netFare = adultPrice-adultTax
            cabin = 'X'
            isChange = 1
            getTime = time.time()


            #增加套餐价格
            price_dict = {
                'LIGHT': 0,
                'EASY': 0,
                'FLEX': 0,
            }
            if adultPrice != 0:
                price_dict['EASY'] = adultPrice + 76
                price_dict['FLEX'] = adultPrice + 76 + 87
            segments = [
                [price_dict.get('EASY'), maxSeats],
                [price_dict.get('FLEX'), maxSeats],
            ]

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
            item['segments'] = json.dumps(segments)
            item['getTime'] = getTime
            yield item
            # print item







    def get_task(self):
        inputFile = open(os.path.join('utils', 'BJ.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 1
        add_num = random.randint(1, 20)
        for i in range(1, 60, days):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y-%m-%d')
            for data in datas:
                if not data or not len(data):
                    continue
                yield (data[0], data[1], _dt)
                # task = [('VKO','BGY','2018-10-06'),('BGY','LED','2018-10-06'),('VKO','PSA','2018-10-06')]
                # for i in task:
                #     yield i

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-' * 40)
        print(failure.value)
        yield failure.request


#爬取的网页端，需要翻墙，且封IP,（这个是一天的任务）
# class BjSpider(scrapy.Spider):
#     name = 'bj'
#     allowed_domains = ['nouvelair.com']
#     start_urls = ['https://booking.nouvelair.com/web/RezvEntry.xhtml?language=en']
#     version = 1.0
#     task = []
#     isOK = True
#     custom_settings = dict(
#         DOWNLOADER_MIDDLEWARES={
#             'wow_spider.middlewares.StatisticsItem': 400,
#             # 'wow_spider.middlewares.ProxyMiddleware': 200,
#             'wow_spider.middlewares.BJCookieMiddleware': 300,
#         },
#         DOWNLOAD_TIMEOUT=20,
#         # LOG_LEVEL = 'DEBUG',
#         PROXY_TRY_NUM=3,
#         # COOKIES_ENABLED=True,
#         INVALID_TIME=45,
#         CONCURRENT_REQUESTS=10,
#         SEAT=3,
#         # ITEM_PIPELINES={
#         #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
#         # },
#         HEADERS={
#             'origin': "https://booking.nouvelair.com",
#             'upgrade-insecure-requests': "1",
#             'content-type': "application/x-www-form-urlencoded",
#             'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
#             'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
#             'referer': "https://booking.nouvelair.com/web/Availability.xhtml",
#             'accept-encoding': "gzip, deflate, br",
#             'accept-language': "zh-CN,zh;q=0.9",
#             # 'cookie': "_ga=GA1.2.1041212038.1541410126; _gid=GA1.2.1163726653.1541410126; SESS928815293dbac09712321be78f004202=VCqWBQ3vEN-KrjW1BqI69Jcax4Vq9H9YsTvY8Tfemro; ckPAXpersist=!jqICmjupBFTdIDIiEP5Ysl9+8I1IRIH7TyKsOLNoVpoQV//ubEZXVKrgrB4/CTrS8uerW3rgT02OLxM=; GCLB=CNSil-ys-pXc3wE; SSESS928815293dbac09712321be78f004202=SMO9BIbigG84e8VTlARiw1x_pxEFqTe0pGaQKfsvO5w; _gat_UA-16382628-1=1; ; JSESSIONID=9B5177373CA7C4D8C2DC0D277DE029D4;  _gat=1"
#             # 'cookie': "_ga=GA1.2.1041212038.1541410126;"
#             #           " _gid=GA1.2.1163726653.1541410126;"
#             #           " SESS928815293dbac09712321be78f004202=VCqWBQ3vEN-KrjW1BqI69Jcax4Vq9H9YsTvY8Tfemro; "
#             #           "ckPAXpersist=!jqICmjupBFTdIDIiEP5Ysl9+8I1IRIH7TyKsOLNoVpoQV//ubEZXVKrgrB4/CTrS8uerW3rgT02OLxM=; "
#             #           "GCLB=CNSil-ys-pXc3wE; "
#             #           "SSESS928815293dbac09712321be78f004202=SMO9BIbigG84e8VTlARiw1x_pxEFqTe0pGaQKfsvO5w;"
#             #           " _gat_UA-16382628-1=1; ; "
#             #           # "JSESSIONID=9B5177373CA7C4D8C2DC0D277DE029D4; "
#             #           "JSESSIONID=81510E36FB9BB27582BF3DC6D8B6D873; "
#             #           " _gat=1",
#             'cookie':
#                 # 'JSESSIONID=285E6140A44CB7FC93227D037D71E206;'
#                 'SSESS928815293dbac09712321be78f004202=KbZ6rc6omhBshyUvxwgMIjWgOQ3OZsOgwqGM7WCR3cU;'
#                 'ckPAXpersist=!+4JZypUKm1Jz4NQiEP5Ysl9+8I1IRJObMMRgz1RvAp0kbpFxMYn1OFiOj8UcRJmp/IuobNh3VvurqMA=;'
#                 'GCLB=CO2WrrCC24q7Qw;'
#                 '_ga=GA1.2.603373243.1541580550;'
#                 '_gid=GA1.2.1460705222.1541580550;'
#                 '_fbp=fb.1.1541580552862.1804073294;',
#             'Pragma': 'no-cache',
#             'Cache-Control': 'no-cache',
#
#
#
#
#         },
#         CITYLIST={
#             u'Algiers - Houari Boumediene': 'ALG',
#             u'Berlin - Tegel': 'TXL',
#             u'Djerba - Zarzis': 'DJE',
#             u'Düsseldorf': 'DUS',
#             u'Frankfurt - am Main': 'FRA',
#             u'Hannover - Langenhagen': 'HAJ',
#             u'Leipzig - Halle': 'LEJ',
#             u'Lille - Lesquin': 'LIL',
#             u'Lyon - Saint Exupéry': 'LYS',
#             u'Marseille - Provence': 'MRS',
#             u'Monastir - Habib Bourguiba': 'MIR',
#             u'Munich - Franz Josef Strauß': 'MUC',
#             u'Nantes - Atlantique': 'NTE',
#             u"Nice - Cote d'Azur": 'NCE',
#             u'Paris - Charles de Gaulle': 'CDG',
#             u'Stuttgart': 'STR',
#             u'Toulouse - Blagnac': 'TLS',
#             u'Tunis - Carthage': 'TUN'},
#         #设置100是找不到有票的航班DUSMIR
#         OTHERFEE={
#             'CDGMIR':11,"TLSTUN":2,"TUNCDG":11,
#             "MIRDUS":11,"STRMIR":11,"DUSDJE":100,
#             "DJEHAD":100,"LEJMIR":11,"DJEDUS":100,
#             "STRDJE":100,"DUSMIR":11,"CDGTUN":11,
#             "MIRLEJ":11,"MIRCDG":11,"MIRNCE":11,
#             "MIRDJE":100,"MIRHAJ":11,"MIRTXL":11,
#             "MIRTUN":100,"MIRSTR":11,"TUNNCE":11,
#             "TUNLYS":11,"TUNMIR":100,"CDGDJE":11,
#             "TUNTLS":11,"DJEMIR":100,"MIRMUC":11,
#             "DJEHAJ":100,"DJELYS":11,"LYSMIR":11,
#             "MIRNTE":100,"HAJMIR":11,"TUNMRS":11,
#             "NCETUN":11,"DJECDG":11,"NTEDJE":11,
#             "DJELEJ":100,"DJEMUC":11,"TUNALG":12,
#             "LYSTUN":11,"MRSTUN":11,"DJESTR":100,
#             "NTETUN":11,"TXLMIR":11,"DJETXL":100,
#             "ALGTUN":94,"DJENTE":11,"LYSDJE":11,
#             "TUNNTE":11,"MUCMIR":11,
#         }
#     )
#
#     def __init__(self, *args, **kwargs):
#         cls = self.__class__
#         super(cls, self).__init__(*args, **kwargs)
#         self.portCitys = dataUtil.get_port_city()
#
#     def start_requests(self):
#         permins = 0
#         print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
#         while True:
#             result = pubUtil.getUrl('BJ', 5)
#             if not result:
#                 logging.info('get task error')
#                 time.sleep(10)
#                 continue
#             for data in result:
#                 (dt, dep, to) = pubUtil.analysisData(data)
#             # for i in range(1):
#             # for data in self.get_task():
#             #     dep, to, dt = data
#             #     dt,dep,to= '2018-11-17','DUS','MIR'
#                 print(dep, to, dt)
#                 seat = self.custom_settings.get('SEAT')
#                 # payload = {'FlightSearch': 'FlightSearch',
#                 #            'adult':seat,
#                 #            'arrPort': to,
#                 #            'child': '0',
#                 #            'currency': 'TND',
#                 #            'depPort': dep,
#                 #            'departureDate': re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\3%5C\2%5C\1', dt),
#                 #            'infant': '0',
#                 #            'j_idt56': 'TND',
#                 #            'javax.faces.partial.render': 'flightGrid0+filter_0',
#                 #            'sortFlights': 'price_0_0',
#                 #            'tripType': 'ONE_WAY'}
#                 payload = {'adult': seat,
#                      'arrPort': to,
#                      'child': '0',
#                      'currency': 'DKK',
#                      'dateFormat': 'dd%2FMM%2Fyyyy',
#                      'depPort': dep,
#                      'departureDate': re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\3%2F\2%2F\1', dt),
#                      'infant': '0',
#                      'language': 'en',
#                      'prefferedCabinClass': '',
#                      'tripType': 'ONE_WAY'}
#                 body = ''
#                 for key in payload:
#                     body = body + key  + '=' + str(payload.get(key)) + '&'
#
#                 invalid = {
#                     'date': dt.replace('-', ''),
#                     'depAirport': dep,
#                     'arrAirport': to,
#                     'mins': self.custom_settings.get('INVALID_TIME'),
#                 }
#                 meta_data = dict(
#                     invalid=invalid,
#                     payload=body,
#                     aaa=(dep, to, dt),
#                     dep_to_admintax=[dep,to]
#                 )
#                 yield scrapy.Request(self.start_urls[0],
#                                      callback=self.parse,
#                                      method='POST',
#                                      headers=self.custom_settings.get('HEADERS'),
#                                      meta={'meta_data': meta_data},
#                                      body=body,
#                                      errback=self.errback
#                                      )
#
#     def parse(self, response):
#         # print(response.text)
#         # self.isOK = True
#         results = response.xpath("//div[@class='flight-details false']")
#         flight_no = response.xpath('//*[@class="no-filter-no-cry"]/text()').extract()
#         if len(flight_no) > 0 :
#             # print "not flight today"
#             return
#         if not results:
#             print "request again"
#             yield scrapy.Request(self.start_urls[0],
#                                  callback=self.parse,
#                                  method='POST',
#                                  headers=self.custom_settings.get('HEADERS'),
#                                  meta={'meta_data': response.meta.get("meta_data")},
#                                  body=response.meta.get("meta_data").get("payload"),
#                                  errback=self.errback
#                                  )
#             return
#         # print(results)
#         #分析每个航班
#         for result in results:
#             #判断中转
#             change = result.xpath('.//div[@class="modal-dialog"]/div[@class="modal-content"]/div[2]').extract()
#             if len(change) > 2:
#                 print "is change"
#                 return
#             flight_number_date = result.xpath(".//div[@class='flight-modal-body']/table")
#             flight_number = flight_number_date.xpath('./tr[1]/td[2]/text()').extract()[0].split('-')
#             carrier = flight_number[0]
#             flightNumber = carrier + flight_number[1]
#             dep_to_admintax = response.meta.get('meta_data').get('dep_to_admintax')
#             dep_airport = results.xpath(".//*[@class='departure-airport']/text()").extract()[0]
#             arr_airport = results.xpath(".//*[@class='arrival-airport']/text()").extract()[0]
#             depAirport = self.custom_settings.get("CITYLIST").get(dep_airport,"Unknown")
#             arrAirport = self.custom_settings.get("CITYLIST").get(arr_airport,"Unknown")
#             if depAirport == "Unknown" or arrAirport == "Unknown":
#                 print "error",'7'*66
#                 return
#
#
#             dep_time_str = flight_number_date.xpath('./tr[3]/td[2]/text()').extract()[0]
#             dep_tupletime = time.strptime(dep_time_str, '%d/%m/%Y %H:%M')
#             depTime = time.mktime(dep_tupletime)
#             arr_time_str = flight_number_date.xpath('./tr[5]/td[2]/text()').extract()[0]
#             arr_tupletime = time.strptime(arr_time_str, '%d/%m/%Y %H:%M')
#             arrTime = time.mktime(arr_tupletime)
#             price = result.xpath('normalize-space(.//div/div[2]/span)').extract()[0].replace(',','')
#             if price == "Stopover at:":
#                 return
#             currency = result.xpath('normalize-space(.//div/div[2]/span[2])').extract()[0]
#             #添加管理税
#             admintax = self.custom_settings.get("OTHERFEE").get(depAirport+arrAirport,101)
#             if admintax == 101:
#                 print "Unknown management routes"
#             maxSeats = result.xpath('normalize-space(.//div/span[@class="last-seat"]/text())').extract()
#             if not maxSeats[0]:
#                 maxSeats = 9
#             else:
#                 maxSeats = int(re.compile('\d').search(maxSeats[0]).group())
#             seta_no = result.xpath("./div[2]/div/div/span").extract()
#             if currency == "No Seats" or seta_no:
#                 currency = "RPG"
#                 adultPrice = 0
#                 maxSeats = 0
#             else:
#                 try:
#                     adultPrice = float(price) + admintax
#                 except:
#                     print depAirport,arrAirport,price,'6'*66
#                     # print response.text
#                     traceback.print_exc()
#                     yield scrapy.Request(self.start_urls[0],
#                                          callback=self.parse,
#                                          method='POST',
#                                          headers=self.custom_settings.get('HEADERS'),
#                                          meta={'meta_data': response.meta.get("meta_data")},
#                                          body=response.meta.get("meta_data").get("payload"),
#                                          errback=self.errback
#                                          )
#                     return
#                 # maxSeats = self.custom_settings.get('SEAT')
#             #请求出现EUR货币重新请求
#             if currency in ["EUR","TND"]:
#                 print "currency is EUR,request again"
#                 yield scrapy.Request(self.start_urls[0],
#                                      callback=self.parse,
#                                      method='POST',
#                                      headers=self.custom_settings.get('HEADERS'),
#                                      meta={'meta_data': response.meta.get("meta_data")},
#                                      body=response.meta.get("meta_data").get("payload"),
#                                      errback=self.errback
#                                      )
#                 return
#             adultTax = 0
#             netFare = adultPrice-adultTax
#             cabin = 'X'
#             isChange = 1
#             getTime = time.time()
#
#
#             item = WowSpiderItem()
#             item['flightNumber'] = flightNumber
#             item['depTime'] = depTime
#             item['arrTime'] = arrTime
#             item['fromCity'] = self.portCitys.get(depAirport, depAirport)
#             item['toCity'] = self.portCitys.get(arrAirport, arrAirport)
#             item['depAirport'] = depAirport
#             item['arrAirport'] = arrAirport
#             item['currency'] = currency
#             item['adultPrice'] = adultPrice
#             item['adultTax'] = adultTax
#             item['netFare'] = netFare
#             item['maxSeats'] = maxSeats
#             item['cabin'] = cabin
#             item['carrier'] = carrier
#             item['isChange'] = isChange
#             item['segments'] = '[]'
#             item['getTime'] = getTime
#             yield item
#             # print item
#
#
#
#
#
#
#
#     def get_task(self):
#         inputFile = open(os.path.join('utils', 'BJ.csv'), 'rU')
#         reader = csv.reader(inputFile)
#         datas = list(reader)
#         inputFile.close()
#         thisday = datetime.now() + timedelta(days=5)
#         # #倒序输出
#         # datas = datas[::-1]
#         # 打乱顺序
#         random.shuffle(datas)
#         days = 1
#         add_num = random.randint(1, 20)
#         for i in range(1, 60, days):
#             _date = thisday + timedelta(days=i)
#             _dt = _date.strftime('%Y-%m-%d')
#             for data in datas:
#                 if not data or not len(data):
#                     continue
#                 yield (data[0], data[1], _dt)
#                 # task = [('VKO','BGY','2018-10-06'),('BGY','LED','2018-10-06'),('VKO','PSA','2018-10-06')]
#                 # for i in task:
#                 #     yield i
#
#     def errback(self, failure):
#         self.log('error downloading....', 40)
#         self.isOK = False
#         print('-' * 40)
#         print(failure.value)
#         yield failure.request

