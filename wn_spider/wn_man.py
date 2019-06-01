# -*- coding: utf-8 -*-
# 主文件
# 2019-03-08
# by hyn

from selenium import webdriver
import urllib, logging, requests
import json
from utils import pubUtil, dataUtil
import time
import traceback
import settings

# logging基本配置
logging.basicConfig(
    # filename='jq-spider-api.log', filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s")


class WnSpider:
    allowed_domains = ['southwest.com']
    start_urls = ['https://www.southwest.com/air/booking/select.html?']
    # moblie url
    # start_urls = ['https://mobile.southwest.com/air/booking/shopping']
    carrier = 'WN'
    version = 1.0
    name = 'wn'
    task = []
    isOK = True
    # 等待网页加载15秒
    timeout = 15

    buffer = []
    st_time = time.time()
    count = 0

    # 初始化
    def __init__(self, name, num=1, proxy=1, local=1):

        self.num = num
        self.ADT = 3
        self.now = 0
        self.permins = 0

        # 通过机场获取城市
        self.host_name = name
        self.num = num
        self.city_ports = dataUtil.get_port_city()
        self.local = local

    # 配置浏览器参数
    def get_google(self):
        chrome_options = webdriver.ChromeOptions()
        prefs = {"profile.managed_default_content_settings.images": 2}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--proxy-server=127.0.0.1:8080')
        chrome_options.add_argument("--ignore-certificate-errors")
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-web-security')
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    # 配置心跳，任务参数
    def heart_task(self):

        result_iter = None
        # 需要加查询判断
        while True:

            try:
                if self.local:
                    if not result_iter:
                        result_iter = pubUtil.get_task(self.name, days=10)
                    result = next(result_iter)
                else:
                    result = json.loads(
                        requests.get(settings.GET_TASK_URL + 'carrier=' + self.name, timeout=60).text).get('data')
            except Exception as e:
                logging.error(e)
                result = None

            if result is None:
                logging.info('Date is None!')
                logging.info('Waiting...')
                time.sleep(16)
                continue
            for data in result:
                # 开始请求
                self.start_requests(data)

    # 开始请求
    def start_requests(self, data):

        driver = self.get_google()

        try:

            # 传入任务数据处理
            input_data = data.split(":")
            from_city = input_data[0][0:3]
            to_city = input_data[0][-3:]
            dep_time_day = input_data[1][-2:]
            dep_time_month = input_data[1][4:6]
            dep_time_year = input_data[1][0:4]
            count = input_data[2]

            # 测试传入数据处理
            logging.info("###input data: " + from_city + "-" + to_city + "-" +
                         dep_time_year + dep_time_month + dep_time_day + "-" + count)

            # 请求地址字典
            url_temp = {
                'adultPassengersCount': str(self.ADT),
                'departureDate': dep_time_year + '-' + dep_time_month + '-' + dep_time_day,
                'departureTimeOfDay': 'ALL_DAY',
                'destinationAirportCode': to_city,
                'fareType': 'USD',
                'int': 'HOMEQBOMAIR',
                'originationAirportCode': from_city,
                'passengerType': 'ADULT',
                'reset': 'true',
                'returnDate': '',
                'returnTimeOfDay': 'ALL_DAY',
                'seniorPassengersCount': '0',
                'tripType': 'oneway',
            }

            request_url = '%s%s' % (self.start_urls[0], urllib.parse.urlencode(url_temp))
            print('# url', request_url)
            driver.get(request_url)
            time.sleep(260)

            driver.close()
            return

        except:
            logging.info('# timeout')
            driver.close()
            return

# 本地测试
if __name__ == '__main__':

    name='test'
    num=1
    proxy=1
    local=1
    wn = WnSpider(name=argv[1], num=num, proxy=proxy, local=local)
    # wn.heart_task()
    wn.start_requests()

# if __name__ == '__main__':
#     import sys
#
#     argv = sys.argv
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
#     wn = WnSpider(name=argv[1], num=num, proxy=proxy, local=local)
#     wn.heart_task()
