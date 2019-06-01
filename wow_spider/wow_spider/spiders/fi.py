# -*- coding: utf-8 -*-
import scrapy,re,time,json,logging,os,csv,random,traceback,sys
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta
from jsonpath import jsonpath
from utils import dataUtil
from utils import pubUtil


class FiSpider(scrapy.Spider):
    name = 'fi'
    allowed_domains = ['icelandair.com']
    start_urls = ['https://book.icelandair.com/plnext/icelandairNew/Override.action?source_web=book.icelandair.com']
    version = 1.0
    task = []
    isOK = True
    isJS = True
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 200,
            'wow_spider.middlewares.FIJsMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=30,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=8,
        COOKIES_ENABLED=False,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=10,
        SEAT=3,
        ITEM_PIPELINES={
            'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        },
        JS_URL = "https://book.icelandair.com",
        JS_RANDOM_POSTFIX = '/fieaffqexderyedsqsfetdbufewzbrayexwrqxd.js',
        JS_HEADER1 = {
            'host': "book.icelandair.com",
            'connection': "keep-alive",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            'accept': "*/*",
            'referer': "https://book.icelandair.com/plnext/icelandairNew/Override.action?source_web=book.icelandair.com",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            },
        JS_HEADER2 = {
            'host': "book.icelandair.com",
            'connection': "keep-alive",
            'origin': "https://book.icelandair.com",
            'x-distil-ajax': "zbrftqwv",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            'content-type': "application/javascript",
            'accept': "*/*",
            'referer': "https://book.icelandair.com/plnext/icelandairNew/Override.action?source_web=book.icelandair.com",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cookie': 'D_IID=F715DA45-7692-39C1-BE92-2266DFFC637C; D_UID=F7C1C238-A0FC-308C-9EEE-528CC2CF8F65; D_ZID=2D97761B-571B-3DC3-BC4F-4FADE86A25A1; D_ZUID=85280F0F-D383-319D-8DD7-F98182CF46D6; D_HID=4834BC84-D885-3395-88A7-AE62D771CF2A; D_SID=115.60.63.59:lPw2YoITlZ9hcCm2XrJb9SRubxjhEAEdF5d73pd78/o',
        },
        HEADERS = {
        'origin': "https://www.icelandair.com",
        'upgrade-insecure-requests': "1",
        'content-type': "application/x-www-form-urlencoded",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
        'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        'referer': "https://www.icelandair.com/",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        # 'cookie':'optimizelyEndUserId=oeu1537181011577r0.9940684361405723; _ga=GA1.2.971326795.1537181012; _gid=GA1.2.1846141680.1537181012; ice_uuid=840a1333-d8ea-471e-9df7-793494f2e802; persist%3Aauth={%22valid%22:%22false%22%2C%22isFetching%22:%22false%22%2C%22_persist%22:%22{%5C%22version%5C%22:-1%2C%5C%22rehydrated%5C%22:true}%22}; reduxPersistIndex=[%22persist:auth%22]; D_IID=F715DA45-7692-39C1-BE92-2266DFFC637C; D_UID=F7C1C238-A0FC-308C-9EEE-528CC2CF8F65; D_SID=115.60.63.59:lPw2YoITlZ9hcCm2XrJb9SRubxjhEAEdF5d73pd78/o; _gcl_au=1.1.323827957.1537232962; ice_sessionId=1537232965788; fs_uid=fullstory.com`4GZ42`6655444617003008:5668600916475904; um_jst=2A24CA40A3A4257CC17F6B47852BDCED2D7B04C432B308596761108C8F96B98D; DWM_XSITECODE=5APD5NEW; source_web=book.icelandair.com; citiesSearched=GLA-REK.OW.BWIFI08AA.2018/10/25-.5APD5NEW.US; LAST_SEARCH=flight-YES%3A3-OW-GLA-KEF-20181025-NOT_SET-5-37; D_ZID=91E1B5AD-09AF-33E6-B8BE-AD6C01C24540; D_ZUID=160B4443-A2A7-32A6-AE18-2E5184B6146A; D_HID=2DF29636-C293-379B-ADF8-A0ABC802B46B; _dd1A=AxjnITXPu138-y58mxO6HMGDuOpNZYWtvqcaRfhp6V-CZhrM83sB!-2058136430!1672330260!15371810380311537181071088.8; sessionStart=1537235384343; _gat_tracker0=1; _gat_tracker1=1; _gat_AMADEUS=1; _gat_UA-100058470-1=1'
        # 'cookie':'D_IID=F715DA45-7692-39C1-BE92-2266DFFC637C; D_UID=F7C1C238-A0FC-308C-9EEE-528CC2CF8F65; D_ZID=91E1B5AD-09AF-33E6-B8BE-AD6C01C24540; D_ZUID=160B4443-A2A7-32A6-AE18-2E5184B6146A; D_HID=2DF29636-C293-379B-ADF8-A0ABC802B46B; D_SID=115.60.63.59:lPw2YoITlZ9hcCm2XrJb9SRubxjhEAEdF5d73pd78/o'
        'cookie':'D_SID=115.60.63.59:lPw2YoITlZ9hcCm2XrJb9SRubxjhEAEdF5d73pd78/o; D_ZID=91E1B5AD-09AF-33E6-B8BE-AD6C01C24540',
        },
    )



    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()



    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name,self.name,self.num,permins,self.version))
        while True:
            # result = pubUtil.getUrl('FI', 5)
            # if not result:
            #     logging.info('get task error')
            #     time.sleep(10)
            #     continue
            # for data in result:
            #     (dt, dep, to) = pubUtil.analysisData(data)
            # for i in range(1):
            for data in self.get_task():
                dep, to, dt = data
                # dt,dep,to= '2018-10-25','GLA','KEF'
                print(dep, to, dt)
                seat = self.custom_settings.get('SEAT')
                payload = {
                    'SO_SITE_POINT_OF_SALE': 'BWI',
                    'ADT': seat,
                    'SO_SITE_PROMPT_FEE': 'N',
                    'EMBEDDED_TRANSACTION': 'FlexPricerAvailability',#
                    'E_LOCATION_1': to,
                    'B_DATE_1': '%s0000'%(dt.replace('-','')),
                    'LANGUAGE': 'US',
                    'ARRANGE_BY': 'E',
                    'PRICING_TYPE': 'O',
                    'B_LOCATION_1': dep,
                    'COMMERCIAL_FARE_FAMILY_1': 'OWCOACHEU',#
                    'REFRESH': '0',
                    'DISPLAY_TYPE': '2',
                    'INF': '0',
                    'EXTERNAL_ID': 'US',
                    'SITE': '5APD5NEW',
                    'TRAVELLER_TYPE_1': 'ADT',
                    'TRIP_TYPE': 'O',
                    'CHD': '0',
                }

                invalid = {
                    'date': dt.replace('-', ''),
                    'depAirport': dep,
                    'arrAirport': to,
                    'mins': self.custom_settings.get('INVALID_TIME')
                }
                body =''
                for key in payload:
                    body = body + key + '=' + str(payload.get(key)) + '&'
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
        # print(response.body)
        self.isOK = True
        self.isJS = True
        error = response.xpath('//title/text()')
        if error:
            if error[0].extract() == 'Distil Validate' :
                # self.isOK = False
                self.isJS = False
                print(error[0].extract())
            if error[0].extract() == 'Distil Captcha':
                self.isOK = False
                self.isJS = False
                print(error[0].extract())
            js = re.compile('src="(.*?)" .*?><').search(response.text).group(1)
            self.custom_settings['JS_RANDOM_POSTFIX'] = js
            # print(js)
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=response.meta.get('meta_data').get('payload'),
                                 callback=self.parse,
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback)
            return
        try:
            data = re.compile('config : (.*), pageEngine :',re.S).search(response.text).group(1)
        except:
            print(response.text)
        # try:
        data = json.loads(data)
        # except:
        #     data = re.compile('"Availability":(.*),"FareReview":').search(response.text).group(1)
        #     print('6' * 66)
        #     try:
        #         availability = json.loads(data)
        #     except:
        #         print(response.text)
        # print(type(availability))
        # print(availability)
        availability = jsonpath(data,'$..Availability')
        if not availability:
            print('No flight to day')
            self.task.append(response.meta.get('meta_data').get('invalid'))
            return
        currency = availability[0].get('currencyBean').get('code')
        isChange = 1
        proposedFlightsGroup = availability[0].get('proposedBounds')[0].get('proposedFlightsGroup')
        for proposedFlight in proposedFlightsGroup:
            segments = proposedFlight.get('segments')
            #先判断是否是中转
            if len(segments) >1:
                print('is change')
                continue
            segment = segments[0]
            carrier = segment.get('airline').get('code')
            flightNumber = carrier + str(segment.get('flightNumber'))
            dep_dt_str = segment.get('beginDate')
            dep_tupletime = time.strptime(dep_dt_str, '%b %d, %Y %I:%M:00 %p')
            depTime = time.mktime(dep_tupletime)
            arr_dt_str =segment.get('endDate')
            arr_tupletime = time.strptime(arr_dt_str, '%b %d, %Y %I:%M:00 %p')
            arrTime = time.mktime(arr_tupletime)
            depAirport = segment.get('beginLocation').get('locationCode')
            arrAirport = segment.get('endLocation').get('locationCode')
            #这个ID是定位价格的
            flightId = proposedFlight.get('proposedBoundId')
            #目前还没找到快捷取值方法，先遍历
            recommendationList = availability[0].get('recommendationList')
            final_price = sys.maxint
            maxSeats,netFare,adultTax,adultPrice,cabin= 0,0,0,0,'x'
            for recommendation in recommendationList:
                #先确定ID
                flightGroupList = recommendation.get('bounds')[0].get('flightGroupList')
                for flightGroup in flightGroupList:
                    if flightId == flightGroup.get('flightId'):
                        maxSeats = flightGroup.get('numberOfSeatsLeft')
                        cabin = flightGroup.get('rbd')
                    else:
                        # print('6' * 66)
                        # print(flightId,flightGroup.get('flightId'))
                        continue
                    boundAmount = recommendation.get('bounds')[0].get('boundAmount')
                    adultPrice = float(boundAmount.get('totalAmount'))
                    if adultPrice >= final_price:
                        continue
                    final_price = adultPrice
                    netFare =  float(boundAmount.get('amountWithoutTax'))
                    adultTax =  float(boundAmount.get('tax'))

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
            yield item
            print(item)





    def get_task(self):
        inputFile = open(os.path.join('utils', 'FI.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 1
        add_num = random.randint(1,2)
        for i in range(add_num, 30, days):
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
