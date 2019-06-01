# -*- coding: utf-8 -*-
import os, sys
BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, BASE_DIR)

# Scrapy settings for lamudatech_dev project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'lamudatech_dev'

SPIDER_MODULES = ['lamudatech_dev.spiders']
NEWSPIDER_MODULE = 'lamudatech_dev.spiders'

GET_URL_TIMEOUT = 30


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'lamudatech_dev (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False
RETRY_ENABLED = False
DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

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
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
  'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'lamudatech_dev.middlewares.LamudatechDevSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    'lamudatech_dev.middlewares.StatisticsItem': 400,
    # 'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': None,
    # 'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
}

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
EXTENSIONS = {
   'scrapy.extensions.telnet.TelnetConsole': None,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
   'lamudatech_dev.pipelines.LamudatechDevPipeline': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
# HTTPERROR_ALLOWED_CODES = []

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

GET_TASK_URL_HIGH = 'http://task.jiaoan100.com/buddha/gethightask?'
GET_TASK_URL = 'http://task.jiaoan100.com/buddha/gettask?'
PUSH_TASK_URL = 'http://task.jiaoan100.com/buddha/pushtask?'
# PUSH_DATA_URL_TEST = 'https://www.jiaoan100.com/dx/br/newairline?' # 测试库
PUSH_DATA_URL_TEST = 'http://test.jiaoan100.com/br_test/newairline?' # 测试
PUSH_DATA_URL = {  # url和对应的概率， 概率为 k/sum(PUSH_DATA_URL.values())
   'http://task.jiaoan100.com/br/newairline?': 3,
   'http://stock.jiaoan100.com/br/newairline?': 7,
}
HEARTBEAT_URL = 'http://task.jiaoan100.com/buddha/heartbeat?'
LOG_URL = 'http://dx.jiaoan100.com/br/log?'
GET_CITYPORTS_URL = 'http://dx.spider.jiaoan100.com/br/portcity?'
PROXY_URL = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier='

GET_PROXY_URL = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?'

LOG_LEVEL = 'INFO'
