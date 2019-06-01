#! -*- encoding:utf-8 -*-
import requests, time, json, logging, urllib, sys, traceback
import redis, threading
from ok import is_ok
from multiprocessing import Pool
from urllib import parse

REDIS_SERVER = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
redis_pool = redis.ConnectionPool(host=REDIS_SERVER, port=REDIS_PORT)
daxiangdaili = 'http://pvt.daxiangdaili.com/ip/?'
PROXY_NUM = 20
params = {
    'tid': '555248480592144',
    # 'tid': '558401143968319',
    'num': PROXY_NUM,
    'format': 'json',
    'protocol': 'https',
    'filter': 'on',
    # 'category': 2, # 高匿
    # 'delay': 1, # 响应时间少于一秒的
    # 'foreign': 'only', # 只接受国外代理
}
baidu_test_url = 'https://www.baidu.com'
big_pool_expire_seconds = 20 * 60

# logging基本配置
logging.basicConfig(
    # filename='jq-spider-api.log', filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


def run():
    flag = 0
    filter = True
    api_url = daxiangdaili + parse.urlencode(params)
    while True:
        try:
            db = redis.Redis(connection_pool=redis_pool)
            # 从api请求代理
            response = requests.get(api_url, timeout=60)
            response_dict = json.loads(response.text)
            print(response_dict)
            # self.logger.info(response_dict)

            # 转换成列表套字典
            proxies_pool = ["{host}:{port}".format(host=rec['host'], port=rec['port']) for rec in response_dict]
            logging.info('get %s proxy' % len(proxies_pool))
            # if proxy can visit baid.com, then go to big pool
            for i, host_port in enumerate(proxies_pool):
                proxies = {
                    'http': 'http://%s' % host_port,
                    'https': 'http://%s' % host_port
                }
                logging.info('test %s' % host_port)
                try:
                    response = requests.get(baidu_test_url, proxies=proxies, timeout=3,
                                            headers={"Connection": 'close'})
                    if response.status_code != 200:
                        logging.info('not pass baidu.com,passed')
                        continue
                    logging.info('pass baidu, continue')
                    db.lpush("proxy:big", host_port)
                    db.set("proxy:ex:%s" % host_port, time.time())
                    db.incr("total:daxiang", 1)

                    pre = time.time()
                    is_ok(db, proxies, host_port, 1)
                    print('spend: %s' % (time.time()-pre))

                except Exception as e:
                    # traceback.print_exc()
                    # print(e)
                    logging.info('not pass baidu, next !!!')
                    continue
            if not filter:
                flag += 1
                if flag >= 5:
                    filter = True
                    params['filter'] = 'on'
                    logging.info('add filter')
                    api_url = daxiangdaili + parse.urlencode(params)
            else:
                flag = 0
        except:
            # traceback.print_exc()
            time.sleep(5)
            if filter:
                flag += 1
                if flag >= 5:
                    filter = False
                    logging.info('delete filter')
                    params.pop('filter')
                    api_url = daxiangdaili + parse.urlencode(params)
            else:
                flag = 0


if __name__ == '__main__':
    try:
        num = int(sys.argv[1])
    except:
        print('pls input the num of thread')
        sys.exit()
    p = Pool()
    threads = []
    for i in range(num):
        p.apply_async(run)

    p.close()
    p.join()


