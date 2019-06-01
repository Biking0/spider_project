#! -*- encoding:utf-8 -*-
import requests,time,json,logging,urllib
import redis, traceback
from ok import is_ok

def change_to_int(hms):
    h, m, s = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

ST_TIME = change_to_int('07:25:00')
EN_TIME = change_to_int('22:00:00') # 这个时间内保证有五个ip,其余时间为一个到两个
BASIC_TIME = 0

## logging基本配置
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)
REDIS_SERVER = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
redis_pool = redis.ConnectionPool(host=REDIS_SERVER, port=REDIS_PORT)
baidu_test_url = 'https://www.baidu.com'
big_pool_expire_seconds = 20 * 60

xundaili = 'http://api.xdaili.cn/xdaili-api//greatRecharge/getGreatIp?'
params = urllib.parse.urlencode({
    'spiderId': '89bd012a044a432a8f9efc34deda9156',
    'orderno': 'YZ20182251455no46u5',
    'returnType': 2,
    'count': 1,
})
api_url = xundaili + params

def pushProxy():
    global BASIC_TIME
    db = redis.Redis(connection_pool=redis_pool)
    try:
        # 从api请求代理
        response = requests.get(api_url)
        BASIC_TIME = time.time()
        response_dict = json.loads(response.text).get('RESULT')
        # 转换成列表套字典
        proxies_pool = ["{host}:{port}".format(host=rec['ip'], port=rec['port']) for rec in response_dict]
        for ip_port in proxies_pool:
            proxies = {
                'http': 'http://%s' % ip_port,
                'https': 'http://%s' % ip_port
            }
            response = requests.get(baidu_test_url, proxies=proxies, timeout=3, headers={"Connection": "close"})
            if response.status_code != 200:
                logging.info('not pass baidu.com,passed')
                continue
            db.lpush("proxy:big", ip_port)
            db.set("proxy:ex:%s" % ip_port, time.time())
            db.incr("total:xun_month", 1)

            logging.info('%s pass baidu, continue' % ip_port)

            is_ok(db, proxies, ip_port)

    except Exception as e:
        traceback.print_exc()
        print(e)
        time.sleep(5)

def time_is_valid():
    current_str = time.strftime('%H:%M:%S', time.localtime(time.time()))
    current_int = change_to_int(current_str)
    if current_int >= ST_TIME and current_int <= EN_TIME:
        return True
    return False

if __name__ == '__main__':
    duration = 0.48 * 60
    endTime = time.mktime(time.strptime('2018-04-04', '%Y-%m-%d'))
    while True:
        if time.time() >= endTime:
            break
        if time.time() - BASIC_TIME >= duration:
            pushProxy()
        else:
            time.sleep(5)
