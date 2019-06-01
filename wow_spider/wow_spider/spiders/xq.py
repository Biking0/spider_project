# -*- coding: utf-8 -*-
import scrapy,re,time,json,logging,os,csv,random,traceback
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta, date
from utils import dataUtil
from utils import pubUtil



class XqSpider(scrapy.Spider):
    name = 'xq'
    allowed_domains = ['sunexpress.com']
    start_urls = ['https://www.sunexpress.com']
    version = 1.5
    task = []
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            # 'wow_spider.middlewares.MMProxyMiddleware': 200,
            'wow_spider.middlewares.XQSessionMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=30,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=8,
        COOKIES_ENABLED=False,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=100,
        SEAT ='3',
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },

        URL="https://www.sunexpress.com",
        SESSION_ID_URL='https://www.sunexpress.com/reservation/ibe/booking?mode=searchResultInter&wvm=WVMD&cabinClass=ECONOMY&promoCode=&pointOfPurchase=OTHERS&channel=DEBD&tripType=OW&origin=BSL&destination=ADB&travelDate=%s&adults=1&children=0&infants=0&locale=en',
        HEADERS={
            'origin': "https://www.sunexpress.com",
            'upgrade-insecure-requests': "1",
            'content-type': "application/x-www-form-urlencoded",
            'user-agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36",
            # 'x-devtools-emulate-network-conditions-client-id': "EBC361BA55FD18B8644574240B92ACA0",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            # 'referer': "https://www.sunexpress.com/reservation/ibe/booking?mode=searchResultInter&wvm=WVMD&cabinClass=ECONOMY&promoCode=&pointOfPurchase=OTHERS&channel=DEBD&tripType=OW&origin=AMS&destination=ASR&travelDate=23-Sep-2018&adults=1&children=0&infants=0&locale=en",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            # 'cookie': "Funnel=1; SECURE_SESSION_COOKIEE0AAFE5DA9516467A7EE497BE53045D2.SE_Prod_IBE8=uddggrckgi3e0dju1vsqqdgufmE0AAFE5DA9516467A7EE497BE53045D2.SE_Prod_IBE8; SECURE_SESSION_COOKIEDD40FDCBF17DCE5495B47EAD9D188A83.SE_Prod_IBE8=ijl0g75p9k5i92v8np342rstjcDD40FDCBF17DCE5495B47EAD9D188A83.SE_Prod_IBE8; SECURE_SESSION_COOKIE1AD2AC6A2AB230423B94ED9ACB536A4A.SE_Prod_IBE8=s26dimjb1uut11thjqkoeg88n1AD2AC6A2AB230423B94ED9ACB536A4A.SE_Prod_IBE8; __cfduid=d12305678575fe8674efaf7b719d7bc5b1536291404; __qca=P0-2082775224-1536291441038; BIGipServeriFlyres_SunExpress_Prod_IBE_Pool=!dUNUzJxPTd4cOe6nKKr5uzvnoMdLBjTgdsN+mhTlPq6DrmvZei/CxH7Re1sp4wX26c2G1XdJpO+pYt8=; _ga=GA1.2.1248802134.1536291486; _gid=GA1.2.1074364993.1536291486; ia_c4dc_4313632383136323131303=1; ia_u4pc_4313632383136323131303=1;  _gat_UA-34576261-1=1; accepted_cookie=1",
        },

    )


    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()
        # 获取session需要一个日期，这里生成10天后的日期
        days = date.today() + timedelta(days=10)
        self.custom_settings['SESSION_ID_URL'] = self.custom_settings['SESSION_ID_URL'] % days.strftime('%d-%b-%Y')

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name,self.name,self.num,permins,self.version))
        while True:
            result = pubUtil.getUrl('XQ', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
            # for data in self.get_task():
            #     dep, to, dt = data
                # dt,dep,to= '2018-09-18','AYT','DUS'
                dt_change = datetime.strptime(dt,'%Y-%m-%d').strftime('%d-%b-%Y')
                print(dep, to, dt,dt_change)
                seat = self.custom_settings.get('SEAT')
                payload = {
                    'origin': dep,
                    'adults':seat,
                    'fareRT': '',
                    'flightNumberRT': '',
                    'wvm': 'WVMD',
                    'ibeScreenId': 'IBE000',
                    'bookingSource': '',
                    'fareOW': '',
                    'children': '0',
                    'cabinClass': 'ECONOMY',
                    '_eventId': 'showWtLblResult',
                    'travelDate': dt_change,
                    'destination': to,
                    'fareLevel': '',
                    'deviceType': '',
                    'tripType': 'OW',
                    'channel': 'DEBD',
                    'pointOfPurchase': 'OTHERS',
                    'flightNumberOW': '',
                    'access_token': '',
                    'promoCode': '',
                    'ccType': '',
                    'skyscanner_redirectid': '',
                    'mode': 'searchResultInter',
                    'infants': '0',
                    'flexTrvlDates': ''}
                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                body =''
                for key in payload:
                    body = body + key + '=' + payload.get(key) + '&'
                meta_data = dict(
                    invalid=invalid,
                    payload=body,
                    aaa = (dep, to, dt),
                    flight_time = dt
                )
                yield scrapy.Request(self.start_urls[0],
                                     callback=self.parse,
                                     method='POST',
                                     headers=self.custom_settings.get('HEADERS'),
                                     meta={'meta_data': meta_data},
                                     body=body,
                                     errback=self.errback
                                     )



    def parse(self, response):
        # print('6'*66)
        flights = response.xpath('//*[@data-validation-prefix="Please choose your outbound flight."]')
        # print('1'*66)
        if not flights:
            print('No flight to day')
            return
        # print('2' * 66)
        # print(len(flights))
        for i in range(len(flights)):
            #判断是否中转
            # change = flights[i].xpath('.//*[@class="flight-information float-left"]/text()').extract()
            change = flights[i].xpath('.//*[@class="layover"]').extract()
            # print(change)
            # if len(change) > 2:
            if change:
                # print('3' * 66)
                print('is change')
                continue
            # print('4'*66)
            flight_number = flights[i].xpath('.//*[@class="flight-information float-left"]/text()').extract()[1]
            # print(flight_number)
            flight_numberlist = re.compile(r'\S+').findall(flight_number)
            flightNumber = ''.join(flight_numberlist)
            dep_time_airport = flights[i].xpath('normalize-space(.//*[@class="departure-time float-left"])').extract()[0].split(' ')
            # print(dep_time_airport)
            dt = response.meta.get('meta_data').get('flight_time')
            dep_dt =dt + 'T' + dep_time_airport[0]
            dep_tupletime = time.strptime(dep_dt, '%Y-%m-%dT%H:%M')
            depTime = time.mktime(dep_tupletime)
            depAirport = dep_time_airport[-1]
            #判断是第二天的情况
            arr_time_airport = flights[i].xpath('normalize-space(.//*[@class="arrival-time float-left"])').extract()[0].split(' ')
            if flights[i].xpath('normalize-space(.//*[@class="time-offset"])').extract()[0]:
                arr_dt = pubUtil.time_add_num(dt,1) + 'T' + arr_time_airport[0]
            else:
                arr_dt = dt + 'T' + arr_time_airport[0]
            arr_tupletime = time.strptime(arr_dt, '%Y-%m-%dT%H:%M')
            arrTime = time.mktime(arr_tupletime)
            arrAirport = arr_time_airport[-1]

            #票卖完了
            try:
                # fare_currency = flights[i].xpath('.//*[@name="selectedHiddenFarepos_0"]/@value').extract()[0].split(':')
                fare_currency = flights[i].xpath('normalize-space(.//*[@class="book-inner"]/text())').extract()[0].split(' ')

                adultPrice = float(fare_currency[0].replace('.','').replace(',','.'))
                adultTax = 0
                netFare = adultPrice - adultTax
                currency = fare_currency[-1]
                # currency = re.compile(r'_(\w+)').findall(fare_currency[2])[-1].split('_')[-1]
            except:
                # print(flights[i].xpath('normalize-space(.//*[@class="book-inner"])'))
                # # print(flights[i].xpath('.//*[@name="selectedHiddenFarepos_0"]/@value').extract())
                # print(response.meta.get('meta_data').get('aaa'))
                # print(dep_dt)
                print('flight invalid')
                # self.task.append(response.meta.get('meta_data').get('invalid'))
                adultPrice = 0
                netFare = 0
                adultTax = 0
                currency = 'A'
                # print('4' * 66)
                # traceback.print_exc()
                # continue

            seat = flights[i].xpath('normalize-space(.//*[@class="seats-left"])').extract()[-1]
            seat_num = re.compile(r'\d+').search(seat)

            # print('---------------------------seat:%s%s-------------------------'%(seat_num,seat))
            if not seat_num:
                #没有时座位比较多
                maxSeats = 9
            else:
                maxSeats = seat_num.group()
            if adultPrice == 0:
                maxSeats = 0
            isChange = 1
            aircraftType = ''
            cabin = 'X'
            carrier = flight_numberlist[0]
            duration_data = flights[i].xpath('.//*[@class="duration float-left"]/text()').extract()[0]
            duration = ':'.join(re.compile(r'\d+').findall(duration_data))

            segments = dict(
                flightNumber=flightNumber,
                aircraftType=aircraftType,
                number=1,
                departureTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(depTime)),
                destinationTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(arrTime)),
                airline=carrier,
                dep=depAirport,
                dest=arrAirport,
                seats=maxSeats,
                duration=duration,
                depTerminal=''
            )
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
            yield item
            # print(item)



    def get_task(self):
        inputFile = open(os.path.join('utils', 'XQ.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 1
        for i in range(1, 30, days):
            _date = thisday + timedelta(days=i)
            _dt = _date.strftime('%Y-%m-%d')
            for data in datas:
                if not data or not len(data):
                    continue
                yield (data[0], data[1], _dt)

    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        print('-' * 40)
        print(failure.value)
        yield failure.request
