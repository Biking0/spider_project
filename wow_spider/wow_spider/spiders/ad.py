# -*- coding: utf-8 -*-
import scrapy,re,time,json,logging,os,csv,random,traceback
from wow_spider.items import WowSpiderItem
from datetime import datetime, timedelta
from utils import dataUtil
from utils import pubUtil



class AdSpider(scrapy.Spider):
    name = 'ad'
    allowed_domains = ['voeazul.com.br']
    start_urls = ['https://viajemais.voeazul.com.br/Search.aspx?culture=en-US']
    # start_urls = ['https://viajemais.voeazul.com.br/Availability.aspx']
    version = 1.8
    task = []
    isOK = False
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.ProxyMiddleware': 200,
            # 'wow_spider.middlewares.XQSessionMiddleware': 300,
        },
        DOWNLOAD_TIMEOUT=30,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=8,
        COOKIES_ENABLED=True,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=4,
        SEAT =5,
        # ITEM_PIPELINES={
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        HEADERS_0={
            'origin': "https://viajemais.voeazul.com.br",
            'upgrade-insecure-requests': "1",
            # 'Connection': 'keep - alive',
            'content-type': "application/x-www-form-urlencoded",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'referer': "https://www.voeazul.com.br/en/home",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cookie': "ad_gdpr=0; sticky=two; VisitorIdAunica=undefined; cro_test=true;",
        },
        HEADERS = {
            'origin': "https://www.voeazul.com.br",
            'upgrade-insecure-requests': "1",
            'content-type': "application/x-www-form-urlencoded",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36",
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'referer': "https://www.voeazul.com.br/en/home",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            # 'cookie': "au_vtid=_1537515595615; _stLang=undefined; rxVisitor=1537511734640K4EAC52NVE3RARS0F0VI6PIP9TKR2VR4; ad_gdpr=0; check=true; sticky=two; s_fid=2DB362F2E69200B0-3E2DD8AAB420EF4D; cro_test=true; _ga=GA1.3.177015028.1537515652; _gid=GA1.3.1526282547.1537515652; AMCVS_04EA1613539237590A490D4D%40AdobeOrg=1; sback_browser=0-58808400-15366563477923b1f3b72de77855498b90953bb876ec2b2f1112196942705b9783db8f9468-44534316-1156061131, 16215859239:30034-1537515555; s_cc=true; sback_client=57dad183becd8a522620c05b; sback_customer=$2QUxUXSidFVPh1Mhd2a6dUTkl2bS1ka20kd4lzaHpGZONFNYlFTthlTQBTYVdWbRl1Swk1aBRFUPh3MKl1YqtWW2$12; sback_partner=false; sb_days=1537515656777; sback_pageview=false; prflTudoAzul=Unknown; sback_refresh_wp=no; sticky=two; _funilid=fluxo-compra; cto_lwid=c5c17199-7144-4f8a-a2fc-d4dc4494f634; _hjIncludedInSample=1; sback_pageview=false; order_filter_option=N%C3%A3o%20selecionado; skysales=2416371466.20480.0000; siteLang=es; _spl_pv=8; sback_total_sessions=2; _spl_pv=9; sback_total_sessions=3; ASP.NET_SessionId=vps413edmqusoekp3lihqrdh; click-carousel-date=0; _searchid=1537534043233352460; rxvt=1537536655206|1537515189394; _prevPage=homepage; mbox=PC#212408fee8184ae7a3cd831b102c3147.24_12#1600760453|session#063fe7586c154764bdf954f0a36705d7#1537601695; dtSa=-; dtLatC=1391; utag_main=v_id:0165fb1303c1000b5d2aa230a2ed0306e002206600bd0$_sn:3$_ss:0$_st:1537601634944$dc_visit:3$vapi_domain:voeazul.com.br$ses_id:1537599834867%3Bexp-session$_pn:1%3Bexp-session$dc_event:1%3Bexp-session$dc_region:ap-northeast-1%3Bexp-session; _st_ses=24224228894276645; _sptid=1434; _spcid=1455; _st_cart_script=helper_voeazul.js; _st_cart_url=/; _st_no_user=1; sback_current_session=1; sback_session=5ba4a01e21968f4af732c7a4; AMCV_04EA1613539237590A490D4D%40AdobeOrg=-330454231%7CMCIDTS%7C17796%7CMCMID%7C64252832240803321852458663562603478574%7CMCAAMLH-1538204638%7C3%7CMCAAMB-1538204638%7CRKhpRz8krg2tLO6pguXWp5olkAcUniQYPHaMWWgdJ3xzPWQmdj0y%7CMCOPTOUT-1537607038s%7CNONE%7CMCAID%7CNONE%7CvVersion%7C3.1.2; s_getDSLVisit_s=Less%20than%201%20day; originDestination_searched=Curitiba%20%28CWB%29_Campinas%20%28VCP%29; s_getNewRepeat=1537599839564-Repeat; s_getDSLVisit=1537599839565; s_sq=azul-novo-prod%3D%2526c.%2526a.%2526activitymap.%2526page%253Dhomepage%2526link%253DSearch%252520and%252520buy%2526region%253Dticket-detail%2526pageIDType%253D1%2526.activitymap%2526.a%2526.c%2526pid%253Dhomepage%2526pidt%253D1%2526oid%253DSearch%252520and%252520buy%2526oidt%253D3%2526ot%253DSUBMIT%26azul-novo-dev%3D%2526c.%2526a.%2526activitymap.%2526page%253Dhttps%25253A%25252F%25252Fviajemais.voeazul.com.br%25252FAvailability.aspx%2526link%253DWednesday%25252C%2525203%252520October.%2525201%252520dias%252520ap%2525C3%2525B3s%252520da%252520data%252520selecionada.%252520O%252520valor%252520de%252520passagem%252520mais%252520barato%252520%2525C3%2525A9%252520de%252520%252524%252520166.03%2525203%252520oct%252520wednesday%252520%252524%252520166.03%2526region%253Dbox-depart-flights%2526.activitymap%2526.a%2526.c; dtPC=399833248_276h2",
            'cookie': "ad_gdpr=0; sticky=two; VisitorIdAunica=undefined; cro_test=true;",
            'Cache-Control': 'max-age=0',
            'connection' : 'keep-alive',
        },
        CURRENCY_CACHE={
            u'R$': u'BRL',  # 巴西雷亚尔
            u'$': u'USD',  # 刀
            u'€': u'EUR',  # 英镑
            # u'$': u'EUR',  # 刀
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
            result = pubUtil.getUrl('AD', 5)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)
            # for i in range(1):
            # for data in self.get_task():
            #     dep, to, dt = data
            #     dt,dep,to= '2018-11-07','JJD','CNF'
                print(dep, to, dt)
                seat = self.custom_settings.get('SEAT')
                payload = {
                    'ControlGroupSearch$SearchMainSearchView$TextBoxMarketOrigin1': dep,
                    'ControlGroupSearch$SearchMainSearchView$TextBoxMarketDestination1': to,
                    'ControlGroupSearch$SearchMainSearchView$DropDownListMarketMonth1': re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\1-\2', dt),
                    'ControlGroupSearch$SearchMainSearchView$DropDownListMarketDay1': re.sub(r'(\d{4})-(\d{2})-(\d{2})',r'\3', dt),
                    'ControlGroupSearch$SearchMainSearchView$DropDownListPassengerType_ADT': '5',
                    'ControlGroupSearch$SearchMainSearchView$TextBoxPromoCode': 'CALLCENT',
                    'culture': 'en-US',
                    'ControlGroupSearch$SearchMainSearchView$DropDownListPassengerType_CHD': '0',
                    # 'departure1': '09/29/2018',
                    'ControlGroupSearch$SearchMainSearchView$CheckBoxUseMacDestination1': '',
                    'ControlGroupSearch$SearchMainSearchView$DropDownListPassengerType_INFANT': '0',
                    # 'originIata1': 'CWB',
                    # 'origin1': 'Curitiba (CWB)',
                    'ControlGroupSearch$SearchMainSearchView$CheckBoxUseMacOrigin1': '',
                    'ControlGroupSearch$SearchMainSearchView$RadioButtonMarketStructure': 'OneWay',
                    # 'destinationIata1': 'VCP',
                    # '_authkey_': '106352422A4DEB0810953636A6FBE2079955529786098DE8B0D32416202E380E34C245FA99C431C7C7A75560FDE65150',
                    'ControlGroupSearch$SearchMainSearchView$DropDownListFareTypes': 'R',
                    '__EVENTTARGET': 'ControlGroupSearch$LinkButtonSubmit',
                    # 'destination1': 'Campinas (VCP)',
                    # 'hdfSearchCodeDeparture1': '1N',
                    # 'hdfSearchCodeArrival1': '1N',
                    # "ControlGroupSearch$SearchMainSearchView$DropDownListSearchBy": 'columnView',
                }
                # payload = {
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListPassengerType_ADT': seat,
                #     'hdfSearchCodeArrival1': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$TextBoxMarketOrigin1': dep,
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListMarketMonth1': re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\1-\2', dt),
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$TextBoxMarketDestination1': to,
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListMarketDay1':re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\3', dt),
                #     'faretypes': 'R',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListMarketDay2': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListSearchBy': 'columnView',
                #     '__EVENTTARGET': 'SearchControlGroupAvailabilityView$LinkButtonSubmit',
                #     'NavigationHeaderInputAvailabilityView$MemberLoginAvailabilityView$PasswordFieldPassword': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListFareTypes': 'R',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListMarketMonth2': '',
                #     'pageToken': '',
                #     # 'culture':'en-US',
                #     'loginDomain': 'AZUL_LOGIN',
                #     '_authkey_': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$CheckBoxUseMacOrigin1': '',
                #     'arrival': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListPassengerType_CHD': '0',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$CheckBoxUseMacDestination1': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$DropDownListPassengerType_INFANT': '0',
                #     'hdfSearchCodeArrival2': '',
                #     'NavigationHeaderInputAvailabilityView$MemberLoginAvailabilityView$TextBoxUserID': '',
                #     '__VIEWSTATE': '/wEPDwUBMGRkZ/qdcJAW2QnebbciaZoBYUGCuQI=', 'password-ta': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$RadioButtonMarketStructure': 'OneWay',
                #     'hdfSearchCodeDeparture2': '',
                #     '__EVENTARGUMENT': '',
                #     'departure2': '',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$CheckBoxUseMacOrigin2': '',
                #     'AvailabilityInputAvailabilityView$DropdownListOrderFlights': '0',
                #     'SearchControlGroupAvailabilityView$SearchControlAvailabilityView$CheckBoxUseMacDestination2': '',
                #     'hdfSearchCodeDeparture1': '',
                #     'login-ta': '',
                # }

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
        # print(response.text)
        # print('6'*66)
        self.isOK = True
        error = response.xpath('//title/text()')[0].extract()
        if error == 'Internal Server Error':
            self.isOK = False
            print(error)
            # print(response.text)
            yield scrapy.Request(self.start_urls[0],
                                 method='POST',
                                 headers=self.custom_settings.get('HEADERS'),
                                 body=response.meta.get('meta_data').get('payload'),
                                 callback=self.parse,
                                 meta={'meta_data': response.meta.get('meta_data')},
                                 errback=self.errback)
            return
        flights = response.xpath('//div[@id="tbl-depart-flights"]/div[@class="flight-item"]')
        #当天没有航班加失效
        if len(flights) == 0:
            invalid = response.meta.get('meta_data').get('invalid')
            self.task.append(invalid)
            print('no flight')
            return
        # print('\n'*5)
        # print(response.body)
        # print('\n'*5)
        # print('7' * 66)
        # price = flights[0].xpath('.//td[@class="promo"]//*[@class="price"]')
        # adultPrice_str = price.xpath('./span[@class="fare-price"]/text()').extract()
        # print(flights)
        for flight in flights:
            flight_data = flight.xpath('.//*[@class="detail"]/a')
            #当天没有航班
            # print('7' * 66)
            if not flight_data:
                invalid = response.meta.get('meta_data').get('invalid')
                self.task.append(invalid)
                print('No flight to day')
                return
            # print(type(flight_data[0]))
            flight_dict =flight_data[0]
            carrier = flight_dict.xpath('./@carriercode').extract()[0]
            if len(carrier.split(',')) > 1:
                print('is change')
                continue
            flightNumber = carrier + str(flight_dict.xpath('./@flightnumber').extract()[0])

            # dt = response.meta.get('meta_data').get('flight_time')
            # dt_str = flight.xpath('.//td[@class="promo"]//@std').extract()[0]
            dt = response.meta.get('meta_data').get('flight_time')
            dep_dt_str = flight_dict.xpath('./@departuretime').extract()[0]
            dep_dt = dt + 'T' + dep_dt_str
            dep_tupletime = time.strptime(dep_dt, '%Y-%m-%dT%H:%M')
            depTime = time.mktime(dep_tupletime)
            # 判断第二天的情况
            arr_dt_str = flight_dict.xpath('./@arrivaltime').extract()[0]
            if int(dep_dt_str.split(':')[0]) > int(arr_dt_str.split(':')[0]):
                arr_dt = pubUtil.time_add_num(dt, 1) + 'T' + arr_dt_str
            else:
                arr_dt = dt + 'T' + arr_dt_str
            arr_tupletime = time.strptime(arr_dt, '%Y-%m-%dT%H:%M')
            arrTime = time.mktime(arr_tupletime)
            depAirport = flight_dict.xpath('./@departure').extract()[0]
            arrAirport = flight_dict.xpath('./@arrival').extract()[0]
            aircraftType = flight_dict.xpath('./@equipmenttype').extract()[0]

            duration = dataUtil.time_standard(flight_dict.xpath('./@traveltime').extract()[0])
            # print('9' * 66)
            # print(flightNumber, depTime, arrTime, depAirport, arrAirport)

            # self.attrib(flight_data)

            price = flight.xpath('.//*[@class="flight-price"]')
            if not price:
                print('no seat')
                adultPrice_str = ''
            else:
                adultPrice_str = price[1].xpath('./span[@class="fare-price"]/text()').extract()

            #当没有座位时
            if not adultPrice_str:
                adultPrice = 0
                currency = 'RPG'
                netFare = 0
                adultTax = 0
                maxSeats =0
                print('no seat')
            else:
                # adultPrice = float(adultPrice_str[0].replace('.','').replace(',','.'))
                currency_unit = price.xpath('normalize-space(./span[@class="currency"]/text())').extract()[0]
                # print(currency_unit)
                if currency_unit == '$':
                    adultPrice = float(adultPrice_str[0])
                else:
                    adultPrice = float(adultPrice_str[0].replace('.', '').replace(',', '.'))

                adultTax = 0
                netFare = adultPrice - adultTax
                # print(price.xpath('normalize-space(./span[@class="currency"]/text())').extract())
                currency = self.custom_settings.get('CURRENCY_CACHE').get(currency_unit,currency_unit)
                # 目前暂未发现座位,使用请求的座位
                maxSeats = self.custom_settings.get('SEAT')

            isChange = 1
            cabin= 'X'

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
        inputFile = open(os.path.join('utils', 'AD.csv'), 'rU')
        reader = csv.reader(inputFile)
        datas = list(reader)
        inputFile.close()
        thisday = datetime.now() + timedelta(days=5)
        # #倒序输出
        # datas = datas[::-1]
        # 打乱顺序
        random.shuffle(datas)
        days = 1
        add_num = random.randint(1,20)
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


    def attrib(self,flight_data):
        # 之前的代码.attrib
        flight_dict = flight_data[0].attrib
        # print(flight_dict)
        # 判断中转
        carrier = flight_dict.get('carriercode')
        if len(carrier.split(',')) > 1:
            print('is change')
            return

        flightNumber = carrier + str(flight_dict.get('flightnumber'))

        # dt = response.meta.get('meta_data').get('flight_time')
        dt =  '2018-09-24'
        dep_dt_str = flight_dict.get('departuretime')
        dep_dt = dt + 'T' + dep_dt_str
        dep_tupletime = time.strptime(dep_dt, '%Y-%m-%dT%H:%M')
        depTime = time.mktime(dep_tupletime)
        # 判断第二天的情况
        arr_dt_str = flight_dict.get('arrivaltime')
        if int(dep_dt_str.split(':')[0]) > int(arr_dt_str.split(':')[0]):
            arr_dt = pubUtil.time_add_num(dt, 1) + 'T' + arr_dt_str
        else:
            arr_dt = dt + 'T' + arr_dt_str
        arr_tupletime = time.strptime(arr_dt, '%Y-%m-%dT%H:%M')
        arrTime = time.mktime(arr_tupletime)
        depAirport = flight_dict.get('departure')
        arrAirport = flight_dict.get('arrival')
        aircraftType = flight_dict.get('equipmenttype')

        duration = dataUtil.time_standard(flight_dict.get('traveltime'))
        print(flightNumber, depTime, arrTime, depAirport, arrAirport)
        print('6' * 66)

