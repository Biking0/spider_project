# -*- coding: utf-8 -*-

# Scrapy settings for lmd_spiders project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'lmd_spiders'

SPIDER_MODULES = ['lmd_spiders.spiders']
NEWSPIDER_MODULE = 'lmd_spiders.spiders'


ROBOTSTXT_OBEY = False

DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'


HEARTBEAT_DURATION = 60 * 10

# HTTPERROR_ALLOWED_CODES = [400, 404, 403]

HTTPERROR_ALLOW_ALL = True


# COOKIES_ENABLED = False

DOWNLOADER_MIDDLEWARES = {
   # 'lamudatech_dev.middlewares.LamudatechDevDownloaderMiddleware': 543,
   'lmd_spiders.middlewares.StatisticsItem': 400,
}

CLOSESPIDER_TIMEOUT=60 * 60 * 2

# 请求等待时间
DOWNLOAD_TIMEOUT = 30

ITEM_PIPELINES = {
   'lmd_spiders.pipelines.LmdSpidersPipeline': 300,
}

EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
}


INVALID_TIME = 45

GET_URL_TIMEOUT = 60

LOG_LEVEL = 'INFO'

GET_PORT_CITY_URL = 'http://116.196.117.196/br/portcity?carrier=VY'
GET_TASK_URL = 'http://task.jiaoan100.com/buddha/gettask?'
GET_TASK_URL_HIGH = 'http://task.jiaoan100.com/buddha/gethightask?'
PUSH_TASK_URL = 'http://task.jiaoan100.com/buddha/pushtask?'
HEARTBEAT_URL = 'http://task.jiaoan100.com/buddha/heartbeat?'
# HEARTBEAT_URL = 'http://127.0.0.1:9999/buddha/heartbeat?'
#
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
    segments='s'
)
