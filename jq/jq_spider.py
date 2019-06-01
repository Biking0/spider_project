# coding=utf-8
import time, logging, requests, json, urllib, re, redis, random, sys, traceback, settings
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs, urlencode
# from urlparse import urlparse, parse_qs
from lxml import etree
from fake_useragent import UserAgent
from utils.genProxy import genProxy

# from utils.set_invalid import set_invalid
from utils.process_cookies.cookies_generator import get_cookies
import urllib3
from utils import pubUtil, timeUtil, dataUtil

# from utils.mac_address import get_mac_address

# logging基本配置
logging.basicConfig(
    # filename='jq-spider-api.log', filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


class JQSpider:

    def __init__(self, name, num, proxy, local):
        # self.ua = UserAgent()
        self.city_airport = self._city_airport()

        self.now = 0
        self.session = requests.session()
        self.start_url = 'https://booking.jetstar.com/sg/zh/booking/search-flights?'
        self.task = []
        self.name = name
        self.num = num
        # self.dynamic = True if dynamic else False
        # self.proxy = True if proxy and not dynamic else False
        self.buffer = []
        self.st_time = timeUtil.change_to_int('07:30:00')
        self.en_time = timeUtil.change_to_int('22:00:00')
        # self.genProxy = genProxy() if self.proxy else ''
        self.genProxy = genProxy()
        self.cookie_time = 0
        # self.refreshCookies()
        self.item_num = 0
        self.db = redis.Redis('116.196.83.53', port=6379, db=1)
        self.version = 1.4
        self.ip_sleep = 0
        self.local = local

        urllib3.disable_warnings()

    def refreshCookies(self):
        content = None
        try:
            if self.db.llen('jq_cookies') <= 0:
                content = get_cookies()
            # else:
            #     content = self.db.lpop('jq_cookies')
        except Exception as e:
            # print('55', e)
            content = get_cookies()
        finally:
            dict_cookies = json.loads(content)
            self.bm_sz = 'bm_sz=' + dict_cookies.get('bm_sz')
            self.ak_bmsc = 'ak_bmsc=' + dict_cookies.get('ak_bmsc')
            # self.ASP_NET_SessionId = 'ASP.NET_SessionId=' + dict_cookies.get('ASP.NET_SessionId')
            # print 'bmsz', self.bm_sz
            # print 'ak_bmsc', self.ak_bmsc
            # print 'ASP.NET_SessionId', self.ASP_NET_SessionId
            logging.info('got new cookie')
            # dict_cookies.pop('ASP.NET_SessionId')
            final_cookies = requests.utils.cookiejar_from_dict(dict_cookies, cookiejar=None, overwrite=True)
            self.session.cookies.update(final_cookies)

    # 处理url
    @property
    def start_request(self):
        result_iter = None
        # 需要加查询判断
        while True:
            # if not timeUtil.time_is_valid(self.st_time, self.en_time):
            #     logging.info('Waiting to 07:30:00.....')
            #     time.sleep(5 * 60)
            #     continue
            # data_api = 'http://dx.redis.jiaoan100.com/buddha/gettask?carrier=JX'
            data_api = 'http://task.jiaoan100.com/buddha/gettask?carrier=jx'
            try:
                if self.local:
                    if not result_iter:
                        result_iter = pubUtil.get_task('JQ', days=10)
                    result = next(result_iter)
                else:
                    result = json.loads(requests.get(data_api, timeout=60).text).get('data')
            except Exception as e:
                logging.error(e)
                result = None

            if result is None:
                logging.info('Date is None!')
                logging.info('Waiting...')
                time.sleep(16)
                continue

            airports, _day, day_num = result[0].split(':')
            # day_num='1'
            # print('airports, _day, day_num',airports, _day, day_num)
            FROM, TO = airports.split('-')
            # FROM, TO = ('DAD', 'HKG')
            _day = re.sub(r'(\d{4})(\d{2})(\d{2})', r'\1-\2-\3', _day)
            days = self._get_dates(_day, day_num)
            # print(days)
            # days = ['2019-01-11', '2019-01-12', '2019-01-13']
            for day in days:
                # FROM, TO, day = 'RGN', 'SIN', '2019-01-17'
                query = urlencode({
                    'origin1': FROM,
                    'destination1': TO,
                    # 'flight-type': '1',
                    'departuredate1': day,
                    'adults': str(settings.ADULT_NUM),
                    'children': '0',
                    'infants': '0',
                })
                print(query)
                # set_invalid('JX', FROM, TO, day)
                total_url = self.start_url + query
                # 设置无效
                invalid = {
                    'date': day.replace('-', ''),
                    'depAirport': FROM,
                    'arrAirport': TO,
                    'mins': settings.INVALID_TIME
                }
                # total_url = 'https://www.jetstar.com/au/en/home?origin=CBR&destination=HNL&flight-type=1&selected-departure-date=02-02-2019&adult=1&flexible=1&currency=AUD'
                # yield total_url,invalid
                yield [total_url, invalid]

    # 请求页面
    def spider_worker(self, task):

        url = task[0]
        invalid = task[1]

        # 解析url
        result = parse_qs(urlparse(url).query)

        FROM = result.get('origin1')[0]
        TO = result.get('destination1')[0]
        response = None
        # try:

        bm_sz = 'bm_sz=8FDDAD1500BB3181E007312084B74DA7~QAAQj+I+Fzus4t5nAQAACobLVLvxdiuzn063pNBFkTVgOPQsHzs06YJZFARyCeRdJ4OW1yMTQ6YZZ2KvYv0RGyJrd7irytTbRAKy4DPJf2FR3bV2+Jbl6azq9ffviB7OT/4PCwV+Wo5KWStfFY4PYePeDAdpwHNyJvDddWXmScoVlyjZu6iFn+ff9reRbCd4'
        ak_bmsc = 'ak_bmsc=C0F93DC841F28198100D2E40067EDBAC173EE28F6F5A0000E2AA3E5C93B0C105~plmMZfVTVea4qlzoPlFKLl0JkkWVWIzJCizVuAJtNbqiAz1q3I+qfoNCCCkFwTFwPMYcyf72MggquEHzDTExDlhBtlHUp/QpM2HxFAVbkUFlV2ruGnUAg2KOvSRDs9Krfoci21iS98FZKfl/xaWQKABFi08wDORmmu/KsdJrsvDF7rsacdDGvjm/cZoh41w+zkYmrrBN5StLBRwL4e4vuTFOTYgerIGpxGAEqOEz4wxwKKrLVePd3D7tXDrY/fkHsp'
        session = 'ASP.NET_SessionId=ekkha1fufcilv3fhdgbmricf'

        # bm_sz = self.bm_sz
        # ak_bmsc = self.ak_bmsc
        ua = UserAgent()
        headers_302 = {
            # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'User-Agent': ua.random,
            # self.ua.random,
            # 'referer': ('https://www.google.com/travel/clk/f?t=%s' % int(time.time() * 1000)),
            'referer': 'https://www.jetstar.com/au/en/home?origin=SYD&destination=NRT&flight-type=1&selected-departure-date=01-02-2019&adult=1&flexible=1&currency=AUD',
            # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': bm_sz + ';' + ak_bmsc

        }

        # print 'headers_302', headers_302

        headers_data = {
            # 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
            'User-Agent': ua.random,
            # self.ua.random,
            # 'referer': ('https://www.google.com/travel/clk/f?t=%s' % int(time.time() * 1000)),
            'referer': 'https://www.jetstar.com/au/en/home?origin=SYD&destination=NRT&flight-type=1&selected-departure-date=01-02-2019&adult=1&flexible=1&currency=AUD',
            # 'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            # 'accept-encoding': 'gzip, deflate, br',
            # 'accept-language': 'zh-CN,zh;q=0.9',
            # 'cookie': self.bm_sz + ';' + self.ak_bmsc + ';' + self.ASP_NET_SessionId

        }
        # if self.dynamic:
        #     (proxies, new_headers) = self.genProxy.genProxy()
        #     headers.update(new_headers)
        # elif self.proxy:
        #     ip_port = self.genProxy.getHttpProxy()
        #     proxies = {"http": "http://" + ip_port, "https": "https://" + ip_port}
        # else:
        #     proxies=''
        # url = 'https://booking.jetstar.com/au/en/booking/search-flights?origin1=SYD&destination1=NRT&departuredate1=2019-02-01&adults=1&children=0&infants=0&AutoSubmit=Y&currency=AUD'
        # url = 'https://booking.jetstar.com/au/en/booking/search-flights?origin1=SYD&destination1=BNK&departuredate1=2019-02-02&adults=1&children=0&infants=0&AutoSubmit=Y&currency=AUD'
        # url = 'https://www.jetstar.com/au/en/home?origin=SYD&destination=BNK&flight-type=2&selected-departure-date=07-02-2019&adult=1&flexible=1&currency=AUD'
        #

        # ip_port = genProxy().getHttpProxy()
        # ip_port='ZLy5cF:XkzCmz@181.177.84.107:9852'
        # ip_port = 'lum-customer-zhanghua-zone-static-country-us:latr6o1y65t3@zproxy.lum-superproxy.io:22225'
        # proxies = {"http": "http://" + ip_port, "https": "https://" + ip_port}
        # proxies = {"https": "https://" + ip_port}
        response = self.session.get(url, headers=headers_302, timeout=30, verify=False,
                                    allow_redirects=False)
        # response = self.session.get(url, headers=headers_302, timeout=100, verify=False)
        # print('130', response)

        # url_302 = 'https://booking.jetstar.com/cn/zh/booking/select-flights'
        url_302 = 'https://booking.jetstar.com/au/en/booking/select-flights'
        proxies = {'http': 'http://localhost:8080'}
        response = self.session.get(url_302, headers=headers_data, timeout=30, verify=False,
                                    allow_redirects=False)
        if response.status_code == 403:
            logging.info('Access Denied!')
            self.refreshCookies()
            self.ip_sleep += 1
            if self.ip_sleep > 5:
                logging.info('# sleep 60s')
                time.sleep(60)
                self.ip_sleep = 0

            return
        self.ip_sleep = 0
        # print('134', response)
        self.parse(response.text, FROM, TO, invalid)

        # except IndexError:
        #     if response.content.lower().find('<title>access denied</title>') != -1:
        #         logging.info('Access Denied!')
        #         self.refreshCookies()
        #         # if not self.dynamic and not self.proxy:
        #         #     self.genProxy.getHttpProxy(True)
        #         self.spider_worker(url)
        #         return
        #     # traceback.print_exc()
        #     logging.info(url)
        # logging.info("%s->%s no data,passed" % (FROM, TO))
        # except Exception as e:
        #     # logging.info("%s->%s,%s,%s failed,try again" % (FROM, TO, 'requests.exceptions.Timeout',url))
        #     # traceback.print_exc()
        #     print e
        #     if not self.dynamic and self.proxy:
        #         self.genProxy.getHttpProxy(True)
        #         # self.refreshCookies()
        #         self.spider_worker(url)

    # 解析页面数据
    def parse(self, response, FROM, TO, invalid):
        # logging.info('success get data!')

        from_city = self.city_airport.get(FROM, FROM)
        to_city = self.city_airport.get(TO, TO)

        html = etree.HTML(response)
        # f = open('123.txt', 'w')
        # f.write(html)
        # f.close()

        # try:
        currency = html.xpath('//div[@id="datalayer-data"]/@data-currency-code')[0]
        # currency = html.xpath('//div[@id="datalayer-data"]/@data-currency-code')

        # except Exception as e:
        #     print e
        # print html.xpath('//div')[0].text
        # print 226, html.xpath('//div[@id="tab-economy-SYD-NRT"]')
        try:
            eco_div = html.xpath('//div[@id="economy-%s-%s"]' % (FROM, TO))[0]
        except:
            return
        # print 'eco: ', eco_div
        display_div = eco_div.xpath('.//div[@class=" display-currency-%s"]/div[@class="row"]' % currency)[1:]
        # row = [leg for leg in display_div if not leg.xpath('.//div[contains(@class, "fare__details--leg-1")]')]
        row = [leg for leg in display_div]
        for div in row:
            # 忽略航班已售完的情况
            try:
                item = dict()
                # try:

                seats = div.xpath('.//span[@class="hot-fare"]')
                if len(seats) == 0:
                    maxSeats = 9
                else:
                    maxSeats = seats[0].text.split(' ')[0]

                # 无航班
                flight_info = div.xpath('.//div[@class="price-select__button"]/input/@data-price-breakdown')
                if len(flight_info) == 0:
                    logging.info('# no flight')
                    self.task.append(invalid)
                    return

                dataPrice = div.xpath('.//div[@class="price-select__button"]/input/@data-price-breakdown')[0]
                dataPriceJson = json.loads(dataPrice)
                adultPrice = round(float(dataPriceJson.get('TotalAmountDue')), 2) // settings.ADULT_NUM
                adultPrice = float(dataPriceJson.get('TotalAmountDue')) // settings.ADULT_NUM
                netFare = round(float(dataPriceJson.get('TotalFare')), 2) // settings.ADULT_NUM
                depTime = div.xpath('.//div[@class="price-select__button"]/input/@data-departure-time')[0]  # 出发时间
                arrTime = div.xpath('.//div[@class="price-select__button"]/input/@data-arrival-time')[0]  # 到达时间
                flightNumber = div.xpath('.//div[@class="price-select__button"]/input/@data-flightnumber')[0]  # 航班号
                # 中转
                if '-' in flightNumber:
                    logging.info('# is change')
                    continue
                timegroup_str = div.xpath('.//div[@class="price-select__button"]/input/@id')[0]
                timegroup = re.findall(r'(\d{2}/\d{2}/\d{4} \d{2}:\d{2})', timegroup_str)
                depTimeStamp = time.mktime(time.strptime(timegroup[0], "%m/%d/%Y %H:%M")).__int__()  # 出发时间
                arrTimeStamp = time.mktime(time.strptime(timegroup[1], "%m/%d/%Y %H:%M")).__int__()  # 出发时间

                item.update(dict(
                    adultPrice=adultPrice,
                    netFare=netFare,
                    depTime=depTimeStamp,
                    arrTime=arrTimeStamp,
                    flightNumber=flightNumber,
                    depAirport=FROM,  # 出发机场
                    arrAirport=TO,  # 到达机场
                    cabin='ECO',
                    currency=currency,
                    fromCity=from_city,
                    toCity=to_city,
                    maxSeats=maxSeats,
                    isChange=1,
                    segments='[]',
                    getTime=time.mktime(datetime.now().timetuple()).__int__(),
                ))
                item.update(dict(
                    adultTax=item["adultPrice"] - item["netFare"],  # 税
                    carrier=item["flightNumber"][:2],
                ))
                # except Exception as e:
                #     adultPrice = 0
                #     netFare = 0
                #     maxSeats = 0
                #     flightNumberTag = \
                #         div.xpath(
                #             './/div[contains(@class, "flight-info__flightNubmer")]/div[@class="medium-11"]/strong')[0]
                #     flightNumber = flightNumberTag.text
                #     depTimeTag = div.xpath('.//strong[@class="depaturestation"]')[0]
                #     arrTimeTag = div.xpath('.//strong[@class="arrivalstation"]')[0]
                #     depTimeContent = re.split(r'[\s\,\;\n\t]+', depTimeTag.text)
                #     arrTimeContent = re.split(r'[\s\,\;\n\t]+', arrTimeTag.text)
                #     depDateStr = ' '.join(depTimeContent[1:-1])
                #     arrDateStr = ' '.join(arrTimeContent[1:-1])
                #     depTimeStamp = time.mktime(time.strptime(depDateStr, "%A %d %B %Y %I:%M%p")).__int__()
                #     arrTimeStamp = time.mktime(time.strptime(arrDateStr, "%A %d %B %Y %I:%M%p")).__int__()
                #     print e
                #     continue
                # finally:

                # print(item)
                self.process_item(item)
            except:
                print(FROM + '-->' + TO)
                traceback.print_exc()

    # 入库
    def process_item(self, item):
        self.buffer.append(item)
        if len(self.buffer) >= 5:
            # # 测试库
            # url = '%scarrier=%s' % (settings.PUSH_DATA_URL_TEST, item["carrier"])
            # # 正式库
            # # url = '%scarrier=%s' % (settings.PUSH_DATA_URL, item["carrier"])
            # data = {
            #     "action": "add",
            #     "data": self.buffer
            #
            # }
            # response = requests.post(url, data=json.dumps(data), timeout=2 * 60, verify=False)
            # logging.info("%s,%s" % (response.content, len(self.buffer)))

            url = dataUtil.get_random_url(settings.PUSH_DATA_URL)
            add_success = pubUtil.addData('add', self.buffer, url, self.name, 'JQ')

            self.item_num += len(self.buffer)
            if add_success:
                self.buffer = []
                invalid_success = pubUtil.invalidData('invalid', self.task, url + 'carrier=%s' % 'JQ', self.name)
                if invalid_success:
                    self.task = []

            # 加入心跳
            run_time = time.time()
            if run_time - self.now >= 60:
                permins = self.item_num
                self.item_num = 0

                print(pubUtil.heartbeat('%s' % (self.name),
                                        'jq', '%s' % self.num, permins, self.version))
                self.now = run_time

    # 城市-机场
    @staticmethod
    def _city_airport():
        api = 'http://dx.jiaoan100.com/br/portcity?carrier=JQ'
        response = requests.get(api)
        return json.loads(response.text).get('data')

    @staticmethod
    def _get_dates(day, num):
        start_day = datetime.strptime(day, '%Y-%m-%d')
        dates = []
        # num = 1
        for _day in range(int(num)):
            dates.append((start_day + timedelta(_day)).strftime('%Y-%m-%d'))
        return dates

    def run(self):
        for url in self.start_request:
            try:
                self.spider_worker(url)
            except:
                traceback.print_exc()
                pass


# 无参数测试
name = 'hyn-test'
num = 1
proxy = False
dynamic = False
run = JQSpider(name, '1', proxy, dynamic)
run.run()

# if __name__ == '__main__':
#     import sys, os
#
#     argv = sys.argv
#     # os.system('mitmdump -s ./mitmproxy_js/addons.py')
#     name = argv[1]
#     num = argv[2] if len(argv) > 2 else 1
#     proxy = argv[3] if len(argv) > 3 else False
#     local = argv[4] if len(argv) > 4 else False
#
#     if local:
#         if local.split('=')[0] == 'local':
#             local = 1
#         else:
#             local = 0
#     else:
#         local = 0
#     # dynamic = argv[4] if len(argv) > 4 else False
#     # jq = JQSpider(name=argv[1], num=num, proxy=proxy, dynamic=dynamic)
#     jq = JQSpider(name=argv[1], num=num, proxy=proxy, local=local)
#     jq.run()
