# -*- coding: utf-8 -*-

# Scrapy settings for spiders_wsc project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'spiders_wsc'

SPIDER_MODULES = ['spiders_wsc.spiders']
NEWSPIDER_MODULE = 'spiders_wsc.spiders'



# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'spiders_wsc (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# CONCURRENT_REQUESTS = 32

# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

HEARTBEAT_DURATION = 60 * 10

#  Disable Telnet Console (enabled by default)
TELNETCONSOLE_ENABLED = False

HTTPERROR_ALLOW_ALL = True

#  Enable or disable spider middlewares
#  See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#     'example.middlewares.ExampleSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   'spiders_wsc.middlewares.StatisticsItem': 200,
}

CLOSESPIDER_TIMEOUT = 60 * 60 * 2

GET_URL_TIMEOUT = 60
# CONCURRENT_REQUESTS=1
# 请求等待时间
DOWNLOAD_TIMEOUT = 30

ITEM_PIPELINES = {
   'spiders_wsc.pipelines.SpidersWscPipeline': 300,
}

INVALID_TIME = 45

LOG_LEVEL = 'INFO'

GET_PORT_CITY_URL = 'http://116.196.117.196/br/portcity?carrier=VY'
GET_TASK_URL = 'http://task.jiaoan100.com/buddha/gettask?'
GET_TASK_URL_HIGH = 'http://task.jiaoan100.com/buddha/gethightask?'
PUSH_TASK_URL = 'http://task.jiaoan100.com/buddha/pushtask?'
HEARTBEAT_URL = 'http://task.jiaoan100.com/buddha/heartbeat?'
# HEARTBEAT_URL = 'http://127.0.0.1:9999/buddha/heartbeat?'

PUSH_DATA_URL = {  # url和对应的概率， 概率为 k/sum(PUSH_DATA_URL.values())
   'http://task.jiaoan100.com/br/newairline?': 3,
   'http://stock.jiaoan100.com/br/newairline?': 7,
}

LOG_URL = 'http://dx.jiaoan100.com/br/log?'
PUSH_DATA_NUM = 10
# PUSH_DATA_URL_TEST = 'https://www.jiaoan100.com/dx/br/newairline?' # 测试
PUSH_DATA_URL_TEST = 'http://test.jiaoan100.com/br_test/newairline?'  # 测试
GET_PROXY_URL = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?'

GET_FRALS_TEST = 'http://test.jiaoan100.com/br_test/frals?carrier='  # 获取测试库中的线路图
GET_FRALS = 'http://116.196.117.196/br/frals?carrier='


DEFAULT_REQUEST_HEADERS = {}

KEYS_MAP = dict(
   flight_number='f',
   dep_time='d',
   arr_time='a',
   from_city='fc',
   to_city='tc',
   dep_port='da',
   arr_port='aa',
   currency='c',
   adult_price='ap',
   adult_tax='at',
   net_fare='n',
   max_seats='m',
   cabin='cb',
   carrier='cr',
   is_change='i',
   segments='s',
   get_time='g',
   info='info',
)
