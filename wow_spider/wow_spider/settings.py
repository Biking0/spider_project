# -*- coding: utf-8 -*-

# Scrapy settings for wow_spider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'wow_spider'

SPIDER_MODULES = ['wow_spider.spiders']
NEWSPIDER_MODULE = 'wow_spider.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'wow_spider (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'


HEARTBEAT_DURATION = 60 * 10

HTTPERROR_ALLOW_ALL = True

DOWNLOADER_MIDDLEWARES = {
   # 'lamudatech_dev.middlewares.LamudatechDevDownloaderMiddleware': 543,
   'wow_spider.middlewares.StatisticsItem': 400,
}

CLOSESPIDER_TIMEOUT=60 * 60 * 2

# 请求等待时间
DOWNLOAD_TIMEOUT = 30

ITEM_PIPELINES = {

   'wow_spider.pipelines.LmdSpidersPipeline': 300,
}

EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
}

RETRY_ENABLED = False

INVALID_TIME = 45

GET_URL_TIMEOUT = 60

LOG_LEVEL = 'INFO'

GET_5J_TAX = 'http://test.jiaoan100.com/br_test/dg5jfactor'
GET_IPV4_PROXY = 'http://dx.proxy.jiaoan100.com/proxy/'
GET_PORT_CITY_URL = 'http://116.196.117.196/br/portcity?carrier=VY'
GET_TASK_URL = 'http://task.jiaoan100.com/buddha/gettask?'
PUSH_TASK_URL = 'http://task.jiaoan100.com/buddha/pushtask?'
HEARTBEAT_URL = 'http://task.jiaoan100.com/buddha/heartbeat?'
# HEARTBEAT_URL = 'http://127.0.0.1:9999/buddha/heartbeat?'
#
# PUSH_DATA_URL = { # url和对应的概率， 概率为 k/sum(PUSH_DATA_URL.values())
#     'http://116.196.117.196/br/newairline?': 7,
#     'http://dx.spider2.jiaoan100.com/br/newairline?': 5,
#     'http://dx.jiaoan100.com/br/newairline?': 2,
#     'http://task.jiaoan100.com/br/newairline?': 8
# }
PUSH_DATA_URL = {  # url和对应的概率， 概率为 k/sum(PUSH_DATA_URL.values())
   'http://task.jiaoan100.com/br/newairline?': 3,
   'http://stock.jiaoan100.com/br/newairline?': 7,
}

LOG_URL = 'http://dx.jiaoan100.com/br/log?'
PUSH_DATA_NUM = 10
# PUSH_DATA_URL_TEST = 'https://www.jiaoan100.com/dx/br/newairline?' # 测试
PUSH_DATA_URL_TEST = 'http://test.jiaoan100.com/br_test/newairline?' # 测试
GET_PROXY_URL = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?'

GET_FRALS_TEST = 'http://test.jiaoan100.com/br_test/frals?carrier=' # 获取测试库中的线路图
GET_FRALS = 'http://116.196.117.196/br/frals?carrier='

# Send Email Config
SENDER = [
    '1697160859@qq.com',
    '765171067@qq.com',
    '815704044@qq.com',
]

PWD = [ # qq邮箱第三方授权码
    'hhxbmixpdlpgchec',
    'mfeywdjmgvgobefi',
    'tdwssamzjgfpbcdj',
]

HOST_SERVER = 'smtp.qq.com'

SPIDER_RECEIVERS = [
    'lincc@lamudatech.com',
    'xjb@lamudatech.com',
 ]
# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
COOKIES_ENABLED = False

# 日志邮件地址
LOG_ADDR = 'qiaoliang@lamudatech.com'
LOG_PASSWORD = 'Qq7035854'
# TO_ADDR = ['qiaoliang@lamudatech.com', 'hyn@lamudatech.com', 'lincc@lamudatech.com']
# 测试
TO_ADDR = ['qiaoliang@lamudatech.com']
SMTP_SERVER = ['smtp.exmail.qq.com', 465]

KEYS_SHORT = dict(
    flightNumber='f',
    depTime='d',
    arrTime='a',
    fromCity='fc',
    toCity='tc',
    depAirport='da',
    arrAirport='aa',
    currency='c',
    adultPrice='ap',
    adultTax='at',
    netFare='n',
    maxSeats='m',
    cabin='cb',
    carrier='cr',
    isChange='i',
    getTime='g',
    stopCities='sc',
    failCount='fct',
    info='info',
    segments='s',
    legs='ls'
)
