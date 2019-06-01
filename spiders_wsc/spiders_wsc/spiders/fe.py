# -*- coding: utf-8 -*-
import scrapy
from spiders_wsc.items import SpidersWscItem
import time
from datetime import datetime
from datetime import timedelta
from utils import pub_util, data_util
import re


class FeSpider(scrapy.Spider):
    name = 'fe'
    allowed_domains = ['www.ws.fat.com.tw']
    start_urls = ['https://ws.fat.com.tw/AndroidFlightService/FlightWebService']
    version = 1.1
    task = []
    seats = 3
    is_ok = True

    custom_settings = dict(
        #用于请求第一个时间界面的请求头
        HEADERS_FOR_TIME={
            'SOAPAction': 'http://fat.com.tw/AvailableFlight',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G955N Build/NRD90M)',
            'Host': 'ws.fat.com.tw',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        },
        #用于第二个请求获取详细价格信息的请求头
        HEADERS_FOR_PRICE={
            'Content-Type': 'text/xml;charset=UTF-8',

            'SOAPAction': 'http://fat.com.tw/SearchFare',
            'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G955N Build/NRD90M)',
            'Host': 'ws.fat.com.tw',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'
        },
        # 用于第一个请求获取航班时间信息的请求体
        DATA_FOR_TIME='''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:fat="http://fat.com.tw/">
                   <soapenv:Header/>
                   <soapenv:Body>
                      <fat:AvailableFlight>
                         <fat:departureCity>{}</fat:departureCity>
                         <fat:arrivalCity>{}</fat:arrivalCity>
                         <fat:departureDate>{}</fat:departureDate>
                         <fat:airlineCode>FE</fat:airlineCode>
                         <fat:rbd></fat:rbd>
                         <fat:minPerson>{}</fat:minPerson>
                      </fat:AvailableFlight>
                   </soapenv:Body>
                </soapenv:Envelope>''',
        # 用于第二个请求获取详细价格信息的请求体
        DATA_FOR_PRICE = '''<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
           <soap:Body>
              <SearchFare xmlns="http://fat.com.tw/">
                 <departureCity>{}</departureCity>
                 <arrivalCity>{}</arrivalCity>
                 <trip>1</trip>
                 <departureDate>{}</departureDate>
                 <returnDate></returnDate>
                 <airlineCode>FE</airlineCode>
                 <source>APP</source>
                 <isOnlyTicket>N</isOnlyTicket>
                 <passengerCnt>{}</passengerCnt>
              </SearchFare>
           </soap:Body>
        </soap:Envelope>''',
        #设置并发数
        CONCURRENT_REQUESTS=1,

        DOWNLOADER_MIDDLEWARES={
            'spiders_wsc.middlewares.StatisticsItem': 200,
            # 'spiders_wsc.middlewares.F3TokenMiddleware': 300,
        },


        # ITEM_PIPELINES={
        #     'spiders_wsc.pipelines.SpidersWscPipelineTest': 300,
        # },
    )
    headers_for_time = custom_settings.get('HEADERS_FOR_TIME')
    headers_for_price = custom_settings.get('HEADERS_FOR_PRICE')
    data_for_time = custom_settings.get('DATA_FOR_TIME')
    data_for_price = custom_settings.get('DATA_FOR_PRICE')

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.port_city = data_util.get_port_city()


    def start_requests(self):
        permins = 0
        self.log(pub_util.heartbeat(self.host_name, self.name, self.num, permins, self.version), 20)  # 心跳
        result_iter = None
        while True:
            if hasattr(self, 'local'):
                if not result_iter:
                    result_iter = pub_util.get_task(self.name, st=1, days=30)
                result = next(result_iter)
            else:
                result = pub_util.get_url(self.name, 1)
            if not result:
                self.log('get task error', 30)
                time.sleep(10)
                continue
            for data in result:
                # print(data)
                dt, dep, arr, days = data_util.parse_data(data)
                # dep, arr = 'KHH', 'MZG'
                this_day = datetime.strptime(dt, '%Y%m%d')
                for vary_day in range(int(days)):
                    one_day = (this_day+timedelta(days=vary_day)).strftime('%Y-%m-%d')
                    # one_day = '2019-03-23'
                    body1 = self.data_for_time.format(dep, arr, one_day, self.seats)
                    flight_data = [dep, arr, one_day, self.seats]
                    meta_data = {
                        'flight_data': flight_data,'oneday':one_day
                    }
                    yield scrapy.Request(
                        url=self.start_urls[0],
                        method='POST',
                        body=body1,
                        meta={'meta_data': meta_data},
                        headers=self.headers_for_time,
                        callback=self.parse_time,
                        errback=self.err_back,
                        dont_filter=True,
                    )

    def err_back(self, failure):
        self.log(failure.value, 40)
        # print('6'*66)
        self.log(failure.request.meta.get('proxy'))
        self.is_ok = False
        return failure.request

    #解析获取时间页面的信息
    def parse_time(self, response):
        # print(response.text)
        para = response.meta.get('meta_data').get('flight_data')
        # para_time = response.meta.get('oneday')
        # print('*' * 20)
        # print(para)
        # print(para_time)
        # exit()
        # print('*'*20)
        # print('开始抓取时间界面信息')
        #航班号（开头部分）, eg:FE
        AirlineCode_list = response.xpath('//FlightInfo/AirlineCode/text()').extract()
        # 航班号（数字部分）, 6027:
        FlightNumber_list = response.xpath('//FlightInfo/FlightNumber/text()').extract()
        # 离开城市:TSA
        DepartureCity_list = response.xpath('//FlightInfo/DepartureCity/text()').extract()
        #到达城市：MZG
        ArrivalCity_list = response.xpath('//FlightInfo/ArrivalCity/text()').extract()
        #离开时间：2019-03-07T12:30:00.000+08:00
        DepartureDateTime_list = response.xpath('//FlightInfo/DepartureDateTime/text()').extract()
        #抵达时间：2019-03-07T13:30:00.000+08:00
        ArrivalDateTime_list = response.xpath('//FlightInfo/ArrivalDateTime/text()').extract()
        #<CabinInfoList>标签内容获取



        count = len(AirlineCode_list)

        pattern_one = re.compile('<FlightInfo>(.*?)</FlightInfo>', re.S)
        pattern_two = re.compile('<CabinInfo><RBD>(.*?)</RBD><SeatAmount>(.*?)</SeatAmount></CabinInfo>', re.S)
        all_flight = re.findall(pattern_one, response.text)

        l = []
        for one_flight in all_flight:
            ll = re.findall(pattern_two, one_flight)
            l.append(dict(ll))
        # 注意这一行有问题CabinInfoList为空导致下面117行报错
        # CabinInfoList = response.xpath('//FlightInfos/FlightInfo/CabinInfoList/text()').extract()

        print('# count',count)

        if count:
            for i in range(count):
                item = SpidersWscItem()
                flight_number = AirlineCode_list[i]+FlightNumber_list[i].lstrip('0')
                dep_port = DepartureCity_list[i]
                arr_port = ArrivalCity_list[i]
                from_city = self.port_city.get(DepartureCity_list[i])
                to_city = self.port_city.get(ArrivalCity_list[i])
                #DepartureDateTime_list[i]   eg：2019-03-08T07:35:00.000+08:00 将字符串转为time_tuple
                deptime_tuple = time.strptime(DepartureDateTime_list[i], '%Y-%m-%dT%H:%M:%S.000+08:00')
                #将time_tuple转换为timestamp
                dep_time = time.mktime(deptime_tuple)
                arrtime_tuple = time.strptime(ArrivalDateTime_list[i], '%Y-%m-%dT%H:%M:%S.000+08:00')
                arr_time = time.mktime(arrtime_tuple)
                carrier = AirlineCode_list[i]
                item['flight_number'] = flight_number
                item['dep_port'] = dep_port
                item['arr_port'] = arr_port
                item['from_city'] = from_city
                item['to_city'] = to_city
                item['dep_time'] = dep_time
                item['arr_time'] = arr_time
                item['carrier'] = carrier
                body2 = self.data_for_price.format(para[0], para[1], para[2], self.seats)
                yield scrapy.Request(url=self.start_urls[0],
                                     headers=self.headers_for_price,
                                     method='POST',
                                     body=body2,
                                     callback=self.parse_price,
                                     meta={'item':item, 'cabin':l[i]},
                                     errback=self.err_back,
                                     dont_filter=True,)
        else:
            print('当天无航班')


    def parse_price(self, response):
        # print('$'*20)
        # print(response.status)
        # print('开始获取价格页面信息')
        item = response.meta['item']
        cabin_dic = response.meta['cabin']
        # print(cabin_dic)
        currency = response.xpath('//Currency/text()').extract_first()
        #所有的机票种类，为了提取需要的三种票

        whole_ticket_type_list = response.xpath('//FareInfo/FareName/text()').extract()
        #全部价格列表
        whole_ticket_price_list = response.xpath('//FareAmount/text()').extract()
        #全部舱位信息
        whole_ticket_cabin_list = response.xpath('//RBD/text()').extract()

        #获取需要的三种票型的索引，需要注意'全票'对应了两个索引，所以需要进一步筛选
        type_list = ['好康促銷優惠票', '促銷優惠票', '全票']
        #存储索引信息
        price_cabin = []
        for i, each_type in enumerate(whole_ticket_type_list):
            if each_type in type_list and int(whole_ticket_price_list[i]):
                price_cabin.append([whole_ticket_price_list[i], whole_ticket_cabin_list[i]])


        price_cabin.sort()
        #设置初始参数
        seats = 0
        for price, cabin in price_cabin:
            seats = int(cabin_dic.get(cabin, 0))
            if seats:
                item.update(dict(
                    adult_price=price,
                    cabin=cabin,
                    net_fare=price
                ))
                break
        item.update(dict(
            max_seats=seats
        ))
        item['get_time'] = time.time()
        item['is_change'] = 1
        item['adult_tax'] = 0
        item['currency'] = currency
        yield item






