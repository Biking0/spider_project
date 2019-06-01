# -*- coding: utf-8 -*-
import scrapy, time, json, logging
from utils import pubUtil, dataUtil
from lmd_spiders.items import LmdSpidersItem
from jsonpath import jsonpath
from lmd_spiders import settings


class SlSpider(scrapy.Spider):
    name = 'sl'
    start_urls = 'https://mobile.lionair.co.id/GQWCF_FlightEngine/GQDPMobileBookingService.svc/SearchAirlineFlights'
    task = []
    isOK = True
    carrier = 'SL'
    seats = 6
    version = 1.1

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'Host': 'mobile.lionair.co.id',
            # 'Origin': 'http://mobile.lionair.co.id',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
            'Referer': 'http://mobile.lionair.co.id/var/containers/Bundle/Application/DAA972CB-192A-4655-ABD7-8B1E0E3B8FC5/ThaiLionAir.app/www/index.html',
            'Accept-Language': 'en-us',
            'Accept': '*/*',
        },

        DOWNLOADER_MIDDLEWARES = {
            'lmd_spiders.middlewares.SLWscMiddleware': 300,
            'lmd_spiders.middlewares.StatisticsItem': 200,
        },
        GET_WSC_URL='https://mobile.lionair.co.id/GQWCF_FlightEngine/GQDPMobileBookingService.svc/InitializeGQService',

        GET_WSC_DATA={
            "B2BID": 0,
            "ApplicableTo": "",
            "UserLoginId": "0",
            "CustomerUserID": 230,
            "Language": "en-GB",
            "isearchType": "15",
            "SearchData1": "iOS",
            "SearchData2": "2.6.2"
        },
        # LOG_LEVEL = 'DEBUG'

        # ITEM_PIPELINES={
        #     'lmd_spiders.pipelines.LmdSpidersPipelineTest': 300,
        # },
    )

    def __init__(self, *args, **kwargs):
        super(SlSpider, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()

    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name, self.name, self.num, permins, self.version))
        while True:
            result = pubUtil.getUrl('SL', 1)
            if not result:
                logging.info('get task error')
                time.sleep(10)
                continue
            for data in result:
                (dt, dep, to) = pubUtil.analysisData(data)  # 把获取到的data格式化
                dt_com = data.split(':')[1]
                self.task.append({'date':dt_com,
                                 'depAirport': dep,
                                 'arrAirport': to,
                                 'mins': settings.INVALID_TIME
                                })
                dep = str(dep)
                to = str(to)
                if pubUtil.dateIsInvalid(dt):
                    logging.info('date is invalid ,next~')
                    continue
                dt_stamp = time.mktime(time.strptime(dt,'%Y-%m-%d')) + 8 * 60 * 60
                data_post={
                    "sd": {
                        "Adults": self.seats,
                        "AirlineCode": "",
                        "ArrivalCity": to,
                        "ArrivalCityName": None,
                        "BookingClass": None,
                        "CabinClass": 0,
                        "ChildAge": [],
                        "Children": 0,
                        "CustomerId": 0,
                        "CustomerType": 0,
                        "CustomerUserId": 230,
                        "DepartureCity": dep,
                        "DepartureCityName": None,
                        "DepartureDate": "/Date(%s)/" % int(dt_stamp * 1000),
                        "DepartureDateGap": 0,
                        "DirectFlightsOnly": False,
                        "Infants": 0,
                        "IsPackageUpsell": False,
                        "JourneyType": 1,
                        "PreferredCurrency": "THB",
                        "ReturnDate": "/Date(-2208988800000)/",
                        "ReturnDateGap": 0,
                        "SearchOption": 1
                    },
                    "fsc": "0"
                }
                yield scrapy.Request(method='POST',
                                     url=self.start_urls,
                                     body=json.dumps(data_post),
                                     callback=self.parse,
                                     meta=data_post,
                                     dont_filter=True,
                                     errback=lambda x: self.download_errback(x, data_post))

    def download_errback(self,x,data):
        logging.info('error download:' + 'pls change ip')
        self.isOK = False
        yield scrapy.Request(method='POST',
                             url=self.start_urls,
                             body=json.dumps(data),
                             callback=self.parse,
                             meta=data,
                             dont_filter=True,
                             errback=lambda x: self.download_errback(x, data))

    def parse(self, response):
        response_dict = json.loads(response.body)
        flights = response_dict.get('SearchAirlineFlightsResult')
        # print(flights)
        if not response_dict.get('pSessionID', 1):
            self.isOK = False
            logging.info('ip is invalid...please change the ip')
            data = response.meta
            yield scrapy.Request(method='POST',
                                 url=self.start_urls,
                                 body=json.dumps(data),
                                 callback=self.parse,
                                 meta=data,
                                 dont_filter=True,
                                 errback=lambda x: self.download_errback(x, data))
        else:
            self.isOK = True
        if not flights:
            return
        for flight in flights:
            if flight.get('TotalSegmentsWithStopOver') > 1:
                continue
            depTime = dataUtil.str_to_stamp(flight.get('DepDate') + flight.get('DepTime'))
            arrTime = dataUtil.str_to_stamp(flight.get('ArrDate') + flight.get('ArrTime'))
            depAirport = flight.get('DepCity')
            arrAirport = flight.get('ArrCity')
            flightNumber = flight.get('MACode') + flight.get('FlightNo')
            currency = flight.get('Currency')
            segmentInfo = flight.get('SegmentInformation')[0]
            cabin = segmentInfo.get('SegBookingClass')
            carrier = flight.get('MACode')
            segment = {}
            segment['flightNumber'] = segmentInfo.get('MACode') + flight.get('FlightNo')
            segment['aircraftType'] = segmentInfo.get('AirCraft')
            segment['number'] = 1
            segment['airline'] = segmentInfo.get('OprAirlineCode')
            segment['dep'] = segmentInfo.get('DepCity')
            segment['dest'] = segmentInfo.get('ArrCity')
            segment['duration'] = dataUtil.format_duration(segmentInfo.get('TDuration'))
            segment['departureTime'] = dataUtil.str_date_format(segmentInfo.get('DepDate') + segmentInfo.get('DepTime'))
            segment['destinationTime'] = dataUtil.str_date_format(segmentInfo.get('ArrDate') + segmentInfo.get('ArrTime'))

            lowFlight = flight.get('PromoFlight')
            if not lowFlight: # 找出最低价
                lowFlight = flight.get('EconomyFlight')
                if not lowFlight:
                    lowFlight = flight.get('BusinessFlight')
                    if not lowFlight:
                        lowFlight = flight.get('BusinessFlexiFlight')

            segment['depTerminal'] = jsonpath(lowFlight, '$..TerminalCode')
            tax = jsonpath(lowFlight, '$..TaxPerPax')[0]
            netFare = jsonpath(lowFlight, '$..PricePerPax')[0]
            seats = jsonpath(lowFlight, '$..StrikeoutInfo')[0]
            maxseats = self.seats
            segment['seats'] = maxseats
            item = LmdSpidersItem()
            item['maxSeats'] = maxseats
            item['flightNumber'] = flightNumber
            item['depTime'] = depTime
            item['arrTime'] = arrTime
            item['depAirport'] = depAirport
            item['arrAirport'] = arrAirport
            item['currency'] = currency
            item['cabin'] = cabin
            item['carrier'] = carrier
            item['segments'] = json.dumps([segment])
            item['isChange'] = 1
            item['getTime'] = time.time()
            item['adultPrice'] = netFare + tax
            item['adultTax'] = tax
            item['netFare'] = netFare
            item['fromCity'] = self.portCitys[depAirport]
            item['toCity'] = self.portCitys[arrAirport]
            yield item

