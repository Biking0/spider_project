# -*- coding: utf-8 -*-
import scrapy, requests, json, re
import time
from datetime import datetime, timedelta
# import urlparse
# 兼容Python3
try:
    from urllib import parse
except ImportError:
    import urllib as parse

from lamudatech_dev.items import FlightsItem
from utils.process_airport_city.get_airport_city import get_airport_city
# from utils.airports_rd import get_airports
from utils.push_date import push_date


class AsSpider(scrapy.Spider):
    name = 'as'
    spider_name = 'as'
    start_urls = 'https://m.alaskaair.com/shopping/flights/'
    search_seat = 5
    banned = False
    currency_cache = {
        u'€': u'EUR',
        u'$': u'USD',
        u'£': u'GBP',
    }
    version = 1.1

    cities = {'JFK': 'New York, NY (JFK-Kennedy)', 'YLW': 'Kelowna, BC, Canada (YLW-Ellison Field)',
              'GST': 'Glacier Bay, AK (GST-Gustavus)', 'SIT': 'Sitka, AK (SIT-Sitka)',
              'SUN': 'Sun Valley, ID (SUN-Friedman Memorial)', 'ATL': 'Atlanta, GA (ATL-Hartsfield Intl.)',
              'BOS': 'Boston, MA (BOS-Logan Intl.)', 'OAK': 'Oakland, CA (OAK-Oakland Intl.)',
              'HNL': 'Honolulu, HI (HNL-Honolulu Intl.)', 'XNA': 'Fayetteville, AR (XNA-Northwest Arkansas Regional)',
              'BOI': 'Boise, ID (BOI-Boise Air Terminal)', 'AKN': 'King Salmon, AK (AKN-King Salmon)',
              'LIR': 'Liberia, Costa Rica (LIR-Liberia)', 'BZN': 'Bozeman, MT (BZN-Gallatin Field)',
              'DCA': 'Washington, DC (DCA-Reagan National)', 'ELP': 'El Paso, TX (ELP-El Paso Intl.)',
              'PVR': 'Puerto Vallarta, Mexico (PVR-Gustavo Diaz Ordaz)', 'SAN': 'San Diego, CA (SAN-Lindbergh Field)',
              'DUT': 'Dutch Harbor, AK (DUT-Dutch Harbor)', 'EAT': 'Wenatchee, WA (EAT-Pangborn Field)',
              'SDP': 'Sand Point, AK (SDP-Sand Point)', 'ADK': 'Adak Island, AK (ADK-Adak Island)',
              'SEA': 'Seattle, WA (SEA-Seattle/Tacoma Intl.)', 'FCA': 'Kalispell, MT (FCA-Glacier Park Intl.)',
              'SCC': 'Prudhoe Bay, AK (SCC-Deadhorse)', 'ASE': 'Aspen, CO (ASE-Sardy Field)',
              'BWI': 'Baltimore, MD (BWI-Baltimore Washington)', 'SJD': 'Cabo San Lucas, Mexico (SJD-Los Cabos Intl.)',
              'ICT': 'Wichita, KS (ICT-Dwight D. Eisenhower National)',
              'SAT': 'San Antonio, TX (SAT-San Antonio Intl.)', 'RDU': 'Raleigh, NC (RDU-Raleigh Durham Intl.)',
              'WRG': 'Wrangell, AK (WRG-Wrangell)', 'MRY': 'Monterey, CA (MRY-Monterey Peninsula)',
              'GTF': 'Great Falls, MT (GTF-Great Falls Intl.)', 'ADQ': 'Kodiak, AK (ADQ-Kodiak)',
              'LIH': 'Lihue, HI (LIH-Lihue/Kauai)', 'DFW': 'Dallas-Ft. Worth, TX (DFW-Dallas/Fort Worth Intl.)',
              'SBP': 'San Luis Obispo, CA (SBP-San Luis Obispo)', 'AUS': 'Austin, TX (AUS-Austin/Bergstrom Intl.)',
              'CHS': 'Charleston, SC (CHS-Charleston Intl.)',
              'SJO': 'San Jose, Costa Rica (SJO-San Jose Juan Santamaria)',
              'YAK': 'Yakima, WA (YKM-Yakima Air Terminal)', 'RDM': 'Bend, OR (RDM-Redmond/Bend/Roberts Field)',
              'SJC': 'San Jose, CA (SJC-San Jose Intl.)', 'BNA': 'Nashville, TN (BNA-Nashville Intl.)',
              'UNK': 'Unalakleet, AK (UNK-Unalakleet)', 'LTO': 'Loreto, Mexico (LTO-Loreto)',
              'JAC': 'Jackson Hole, WY (JAC-Jackson Hole)', 'ZIH': 'Ixtapa, Mexico (ZIH-Ixtapa/Zihuatanejo Intl.)',
              'MZT': 'Mazatlan, Mexico (MZT-Gen Rafael Buelna)', 'OMA': 'Omaha, NE (OMA-Eppley Field)',
              'JNU': 'Juneau, AK (JNU-Juneau Intl.)', 'OME': 'Nome, AK (OME-Nome)',
              'PHL': 'Philadelphia, PA (PHL-Philadelphia Intl.)', 'BRW': 'Barrow, AK (BRW-Wiley Post/Will Rogers)',
              'PQI': 'Presque Isle, ME (PQI-Presque Isle)', 'SNA': 'Orange County, CA (SNA-Santa Ana)',
              'YEG': 'Edmonton, AB, Canada (YEG-Edmonton Intl.)', 'YYZ': 'Toronto, ON, Canada (YYZ-Pearson)',
              'SFO': 'San Francisco, CA (SFO-San Francisco Intl.)', 'CDV': 'Cordova, AK (CDV-Mudhole Smith)',
              'PHX': 'Phoenix, AZ (PHX-Sky Harbor Intl.)', 'LAX': 'Los Angeles, CA (LAX-Los Angeles Intl.)',
              'MMH': 'Mammoth Lakes, CA (MMH-Mammoth Lakes)', 'YYC': 'Calgary, AB, Canada (YYC-Calgary Intl.)',
              'ALW': 'Walla Walla, WA (ALW-Walla Walla Regional)', 'ORD': "Chicago, IL (ORD-O'Hare)",
              'PUW': 'Moscow, ID (PUW-Pullman/Moscow Regional)', 'GDL': 'Guadalajara, Mexico (GDL-Miguel Hidalgo)',
              'MEX': 'Mexico City, Mexico (MEX-Juarez Intl.)', 'LAS': 'Las Vegas, NV (LAS-McCarran Intl.)',
              'MKE': 'Milwaukee, WI (MKE-General Mitchell Intl.)', 'BHB': 'Bar Harbor, ME (BHB-Bar Harbor)',
              'MSY': 'New Orleans, LA (MSY-New Orleans Intl.)', 'CMH': 'Columbus, OH (CMH-Port Columbus Intl.)',
              'KOA': 'Kailua, HI (KOA-Keahole)', 'LWS': 'Lewiston, ID (LWS-Nez Perce County Regional)',
              'ZLO': 'Manzanillo, Mexico (ZLO-Intl. Playa de Oro)', 'VDZ': 'Valdez, AK (VDZ-Valdez)',
              'MSP': 'Minneapolis, MN (MSP-Minneapolis/St. Paul Intl.)', 'MSO': 'Missoula, MT (MSO-Missoula County)',
              'FLL': 'Fort Lauderdale, FL (FLL-Hollywood Intl.)', 'DEN': 'Denver, CO (DEN-Denver Intl.)',
              'SMF': 'Sacramento, CA (SMF-Sacramento Intl.)', 'KSM': 'St. Marys, AK (KSM-St. Marys)',
              'DTW': 'Detroit, MI (DTW-Wayne County)', 'BET': 'Bethel, AK (BET-Bethel Municipal)',
              'IAH': 'Houston, TX (IAH-Houston Bush Intercontinental)', 'TUS': 'Tucson, AZ (TUS-Tucson Intl.)',
              'BIL': 'Billings, MT (BIL-Logan Intl.)', 'TPA': 'Tampa, FL (TPA-Tampa Intl.)',
              'HLN': 'Helena, MT (HLN-Helena Regional)', 'BUR': 'Burbank, CA (BUR-Burbank/Glendale/Pasadena)',
              'PDX': 'Portland, OR (PDX-Portland Intl.)', 'YVR': 'Vancouver, BC, Canada (YVR-Vancouver Intl.)',
              'OKC': 'Oklahoma City, OK (OKC-Will Rogers World)', 'FAT': 'Fresno, CA (FAT-Fresno Air Terminal)',
              'MFR': 'Medford, OR (MFR-Medford/Jackson County)', 'FAI': 'Fairbanks, AK (FAI-Fairbanks Intl.)',
              'GEG': 'Spokane, WA (GEG-Spokane Intl.)', 'IAD': 'Washington, DC (IAD-Dulles)',
              'EUG': 'Eugene, OR (EUG-Mahlon Sweet Field)', 'ONT': 'Ontario, CA (ONT-Ontario Intl.)',
              'ENA': 'Kenai, AK (ENA-Kenai)', 'STG': 'St. George Island, AK (STG-St. George Island)',
              'DLG': 'Dillingham, AK (DLG-Dillingham)', 'SNP': 'St. Paul Island, AK (SNP-St. Paul Island)',
              'STL': 'St. Louis, MO (STL-Lambert/St.  Louis Intl.)', 'BDL': 'Hartford, CT (BDL-Bradley Intl.)',
              'HOM': 'Homer, AK (HOM-Homer)', 'YKM': 'Yakima, WA (YKM-Yakima Air Terminal)',
              'ABQ': 'Albuquerque, NM (ABQ-Albuquerque Intl.)', 'KTN': 'Ketchikan, AK (KTN-Ketchikan Intl.)',
              'BLI': 'Bellingham, WA (BLI-Bellingham Intl.)', 'STS': 'Santa Rosa, CA (STS-Santa Rosa)',
              'PBG': 'Plattsburgh, NY (PBG-Plattsburgh AFB)', 'EWR': 'New York, NY (EWR-Newark Intl.)',
              'PSP': 'Palm Springs, CA (PSP-Palm Springs International Airport)',
              'SLC': 'Salt Lake City, UT (SLC-Salt Lake City Intl.)', 'MCO': 'Orlando, FL (MCO-Orlando Intl.)',
              'SBA': 'Santa Barbara, CA (SBA-Santa Barbara Municipal)', 'RNO': 'Reno, NV (RNO-Reno/Tahoe Intl.)',
              'CDB': 'Cold Bay, AK (CDB-Cold Bay)', 'MCI': 'Kansas City, MO (MCI-Kansas City Intl.)',
              'ANC': 'Anchorage, AK (ANC-Anchorage Intl.)', 'MCG': 'McGrath, AK (MCG-McGrath)',
              'PSC': 'Kennewick, WA (PSC-Tri-Cities)', 'LGA': 'New York, NY (LGA-LaGuardia)',
              'ANI': 'Aniak, AK (ANI-Aniak)', 'DAL': 'Dallas, TX (DAL-Love Field)',
              'OTZ': 'Kotzebue, AK (OTZ-Ralph Wien Memorial)', 'PSG': 'Petersburg, AK (PSG-James A. Johnson)',
              'IND': 'Indianapolis, IN (IND-Indianapolis Intl.)', 'OGG': 'Kahului, HI (OGG-Kahului/Maui)',
              'YYJ': "Victoria, BC, Canada (YYJ-Victoria Int'l Airport)"}

    custom_settings = dict(
        DEFAULT_REQUEST_HEADERS={
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'Content-Type': "application/x-www-form-urlencoded",
            'origin': "https://m.alaskaair.com",
            'referer': "https://m.alaskaair.com/shopping/flights",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        },

        # 仅供测试用
        # ITEM_PIPELINES={
        #     'lamudatech_dev.pipelines.LamudatechDevPipelineTest': 300,
        # },

        DOWNLOADER_MIDDLEWARES={
            # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
            # 'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': None,
            # 'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
            'lamudatech_dev.middlewares.StatisticsItem': 400,
            'lamudatech_dev.middlewares.AsProcessProxy': 401,
        },

        CONCURRENT_REQUESTS=1,
        CLOSESPIDER_TIMEOUT=60 * 60 * 2,
        DOWNLOAD_DELAY=2,
        DOWNLOAD_TIMEOUT=16,
        # DEPTH_PRIORITY=1,
        # COOKIES_ENABLED=False,
        HTTPERROR_ALLOWED_CODES=[403],
        # LOG_FILE='log/%s-spider.log' % spider_name,
        # LOG_LEVEL='DEBUG',
        )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.city_airport = get_airport_city()

    def start_requests(self):
        while True:
            result = self.get_task(self.spider_name)
            airports, _date, _num = result[0].split(':')
            dep_code, arr_code = airports.split('-')

            date_array = self._get_dates(_date, int(_num))
            _date = date_array.pop(0)
            _from = self.cities.get(dep_code)
            _to = self.cities.get(arr_code)
            body = {'SaveFields.SelDepOptId': '-1', 'SaveFields.RetShldrSel': 'False', 'SearchFields.IsAwardBooking': 'false',
                    'SearchFields.PriceType': 'Lowest', 'SearchFields.UpgradeOption': 'none',
                    'ClientStateCode': 'HA', 'SaveFields.SelRetOptId': '-1', 'SaveFields.DepShldrSel': 'False',
                    # 'SearchFields.DepartureCity': 'San Francisco, CA (SFO-San Francisco Intl.)',
                    # 'SearchFields.ArrivalCity': 'Portland, OR (PDX-Portland Intl.)',
                    'SearchFields.NumberOfTravelers': self.search_seat, 'SearchFields.SearchType': 'OneWay', 'SearchFields.IsCalendar': 'false',
                    'SearchFields.DepartureCity': _from,
                    'SearchFields.ArrivalCity': _to,
                    'SourcePage': 'Search', 'SearchFields.DepartureDate': _date,
                    }
            yield scrapy.Request(method='POST', url=self.start_urls, body=parse.urlencode(body),
                                 meta={'dep_code': dep_code, 'arr_code': arr_code, '_date': _date,
                                       'date_array': date_array},
                                 callback=self.cookies_parse,
                                 errback=self.errback)

    def errback(self, failure):
        self.log(failure.value, 40)
        self.banned = True
        # time.sleep(8)
        return failure.request

    def cookies_parse(self, response):
        cookies = self._set_cookies(response)
        base_url = 'https://m.alaskaair.com/'
        src = response.xpath('//div[@style="position:fixed; top:0; left:0; display:none"]/img/@src').extract_first()
        appid_url = parse.basejoin(base_url, src)
        headers = {
            'accept': "image/webp,image/apng,image/*,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'referer': "https://m.alaskaair.com/shopping/flights",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
        }
        yield scrapy.Request(url=appid_url, headers=headers, cookies=cookies,
                             callback=self.pxvid_parse,
                             errback=self.errback,
                             meta={'res': response}
                             )

    def pxvid_parse(self, response):
        cookies = self._set_cookies(response)
        cookies.extend(response.request.cookies)
        res = response.meta.get('res')
        res.request.cookies = cookies
        res.request.callback = self.parse
        return self.parse(res)

    def parse(self, response):
        meta = response.meta
        dep_code = meta.get('dep_code')
        arr_code = meta.get('arr_code')
        _date = meta.get('_date')
        date_array = meta.get('date_array')

        if date_array:
            _from = self.cities.get(dep_code)
            _to = self.cities.get(arr_code)
            for _date_s in date_array:
                body = {'SaveFields.SelDepOptId': '-1', 'SaveFields.RetShldrSel': 'False',
                        'SearchFields.IsAwardBooking': 'false',
                        'SearchFields.PriceType': 'Lowest', 'SearchFields.UpgradeOption': 'none',
                        'ClientStateCode': 'HA', 'SaveFields.SelRetOptId': '-1', 'SaveFields.DepShldrSel': 'False',
                        # 'SearchFields.DepartureCity': 'San Francisco, CA (SFO-San Francisco Intl.)',
                        # 'SearchFields.ArrivalCity': 'Portland, OR (PDX-Portland Intl.)',
                        'SearchFields.NumberOfTravelers': self.search_seat, 'SearchFields.SearchType': 'OneWay',
                        'SearchFields.IsCalendar': 'false',
                        'SearchFields.DepartureCity': _from,
                        'SearchFields.ArrivalCity': _to,
                        'SourcePage': 'Search', 'SearchFields.DepartureDate': _date_s,
                        }
                yield scrapy.Request(method='POST', url=self.start_urls, body=parse.urlencode(body),
                                     meta={'dep_code': dep_code, 'arr_code': arr_code, '_date': _date_s},
                                     cookies=response.request.cookies,
                                     callback=self.parse, errback=self.errback)

        flight_day = response.xpath('//div[@class="shoulderSelected"]/input/@value').extract_first()
        optionList = response.xpath('//*[@id="result-0"]/ul/li[div[@class="optionDetail"]/div[@class="clear"]/a/text()="Nonstop"]')
        item = None
        for li in optionList:
            # 航班号
            optionHeader = li.xpath('div[@class="optionHeader"]')
            flight_number = optionHeader.xpath('div[@class="optionHeaderFltNum"]/text()').re(r'\d+')[0]
            # 机场，时间
            optionDetail = li.xpath('div[@class="optionDetail"]')
            dep = optionDetail.xpath('div[@class="optionDeparts"]')
            dep_airport = dep.xpath('div[@class="optionCityCode"]/text()').extract_first()
            dep_time = dep.xpath('div[@class="optionTime"]/div[@class="b"]/text()').extract_first()
            dep_date = flight_day + dep_time
            arr = optionDetail.xpath('div[@class="left"]')
            arr_airport = arr.xpath('div[@class="optionCityCode"]/text()').extract_first()
            arr_time = arr.xpath('div[@class="optionTime"]/div[@class="b"]/text()').extract_first()
            arrivalDaysDifferent = arr.xpath('div[@class="optionTime"]/div[@class="arrivalDaysDifferent"]/text()').re(r'\d')
            if arrivalDaysDifferent:
                num = int(arrivalDaysDifferent[0])
                arr_date = self._add_date(flight_day, num) + arr_time
            else:
                arr_date = flight_day + arr_time
            # 价格
            data_c_l_p = li.xpath('div[@data-c="l"]/@data-p').extract()
            price = float(min(data_c_l_p, key=float))
            # 货币种类
            currency = li.xpath('div[@data-c="l" and @data-p]/div[@class="fareprice"]/text()').re(r'\D+')[0]
            currency = self.currency_cache.get(currency)
            if currency is None:
                continue

            fromCity = self.city_airport.get(dep_airport, dep_airport)
            toCity = self.city_airport.get(arr_airport, arr_airport)

            if dep_code != dep_airport or arr_code != arr_airport:
                print('ft: %s-%s' % (dep_code, arr_code))
                print('da: %s-%s' % (dep_airport, arr_airport))
            item = FlightsItem()
            item.update(dict(
                flightNumber='AS' + flight_number.strip(),  # 航班号
                depTime=int(time.mktime(time.strptime(dep_date, "%m/%d/%Y%I:%M %p"))),  # 出发时间
                arrTime=int(time.mktime(time.strptime(arr_date, "%m/%d/%Y%I:%M %p"))),  # 达到时间
                fromCity=fromCity,  # 出发城市
                toCity=toCity,  # 到达城市
                depAirport=dep_airport,  # 出发机场
                arrAirport=arr_airport,  # 到达机场
                currency=currency,  # 货币种类
                adultPrice=float(price),  # 成人票价
                adultTax=0,  # 税价
                netFare=float(price),  # 净票价
                maxSeats=self.search_seat,  # 可预定座位数
                cabin='E',  # 舱位
                carrier='AS',  # 航空公司
                isChange=1,  # 是否为中转 1.直达2.中转
                segments="NULL",  # 中转时的各个航班信息
                getTime=int(time.time()),
            ))

            yield item

        # 设置失效
        if item is None:
            data = {
                'depAirport': dep_code,
                'arrAirport': arr_code,
                'date': datetime.strptime(_date, "%m/%d/%Y").strftime('%Y%m%d')
            }
            content = push_date(self.settings.get('PUSH_DATA_URL'),
                                params={'carrier': self.spider_name},
                                action='invalid', data_array=[data])
            self.log('[%s] %s-%s no flight.' % (_date, dep_code, arr_code), 20)

    @staticmethod
    def _get_dates(_date, _num):
        dates = []
        for day in range(0, _num):
            dates.append((datetime.strptime(_date, '%Y%m%d') + timedelta(day)).strftime('%m/%d/%Y'))
        return dates

    def get_task(self, carrier):
        task_api = self.settings.get('GET_TASK_URL') + 'carrier=%s' % carrier
        while True:
            try:
                result = json.loads(requests.get(task_api, timeout=180).text).get('data')
            except Exception as e:
                self.log(e, 40)
                time.sleep(8)
            else:
                if not result:
                    self.log('Date is None!\nWaiting...', 40)
                    time.sleep(16)
                    continue
                break
        return result

    # 简单的返回日期加运算
    @staticmethod
    def _add_date(date, num):
        return (datetime.strptime(date, "%m/%d/%Y") + timedelta(num)).strftime("%m/%d/%Y")

    @staticmethod
    def _set_cookies(response):
        set_cookies = response.headers.getlist('Set-Cookie')
        cookie_items = [re.match(r'(.*?)=(.*?);', i).groups() for i in set_cookies]
        cookies = [{u'domain': u'.alaskaair.com', u'secure': False, u'value': unicode(v), u'expiry': None,
                    u'path': u'/', u'httpOnly': False, u'name': unicode(k)} for k, v in cookie_items]
        return cookies
