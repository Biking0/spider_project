# encoding:utf-8
BOT_NAME = 'flybe_spider'

SPIDER_MODULES = ['flybe_spider.spiders']
NEWSPIDER_MODULE = 'flybe_spider.spiders'

ROBOTSTXT_OBEY = False

# 并发与超时
CONCURRENT_REQUESTS = 8

# 请求等待时间
DOWNLOAD_TIMEOUT = 10

GET_URL_TIMEOUT = 60 * 2

#请求延迟
DOWNLOAD_DELAY = 0

JUDGE_DURATION = 60 * 30

HEARTBEAT_DURATION = 60 * 1
TEST_URL = 'https://www.flybe.com/api/fares/day/new/ALC/DSA?depart=ALC&arr=DSA&departing=2018-02-13&returning=&promo-code=&adults=1&teens=0&children=0&infants=0'
DOWNLOADER_MIDDLEWARES = {
   # 'flybe_spider.middlewares.FlybeDownloaderMiddleware': 543,
    'flybe_spider.middlewares.ProxyMiddleware': 500,
    'flybe_spider.middlewares.StatisticsItem': 400,
}

PUSH_DATA_NUM = 15

#设置请求头
DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36',
    'referer': 'https://www.flybe.com/web-app/index.html'
}

ITEM_PIPELINES = {
   'flybe_spider.pipelines.FlybePipeline': 300,
}

#日志处理
LOG_LEVEL = 'INFO'
# LOG_FILE = 'flybe.log'

GET_PROXY_URL = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?'

GET_TASK_URL = 'http://task.jiaoan100.com/buddha/gettask?'
PUSH_TASK_URL = 'http://task.jiaoan100.com/buddha/pushtask?'
HEARTBEAT_URL = 'http://task.jiaoan100.com/buddha/heartbeat?'
PUSH_DATA_URL = 'http://stock.jiaoan100.com/br/newairline?'
LOG_URL = 'http://dx.jiaoan100.com/br/log?'
GET_CITYPORTS_URL = 'http://dx.spider.jiaoan100.com/br/portcity?'
# PUSH_DATA_URL = 'http://test.jiaoan100.com/br_test/newairline?' # 测试
