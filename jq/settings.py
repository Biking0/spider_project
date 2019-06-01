# encoding=utf-8
# JQ
# by hyn
# 2019-01-17


# 查询乘客数
ADULT_NUM = 3

GET_PORT_CITY_URL = 'http://116.196.117.196/br/portcity?carrier=VY'
GET_PROXY_URL = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?'
GET_TASK_URL = 'http://task.jiaoan100.com/buddha/gettask?'
PUSH_TASK_URL = 'http://task.jiaoan100.com/buddha/pushtask?'
HEARTBEAT_URL = 'http://task.jiaoan100.com/buddha/heartbeat?'

# 测试库
PUSH_DATA_URL_TEST = 'http://test.jiaoan100.com/br_test/newairline?'
# 正式库
PUSH_DATA_URL = {  # url和对应的概率， 概率为 k/sum(PUSH_DATA_URL.values())
   'http://task.jiaoan100.com/br/newairline?': 3,
   'http://stock.jiaoan100.com/br/newairline?': 7,
}

LOG_URL = 'http://dx.spider.jiaoan100.com/br/log?'
GET_URL_TIMEOUT = 2 * 60
INVALID_TIME=45
