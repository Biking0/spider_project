#! -*- encoding:utf-8 -*-
import os
import sys
import json
import time
import urllib
import logging
import traceback
import threading
from urllib import parse

import redis
import gevent
import requests

from ok import test_proxy
from multiprocessing import Pool

REDIS_SERVER = '127.0.0.1'
REDIS_PORT = 6379
REDIS_DB = 0
redis_pool = redis.ConnectionPool(host=REDIS_SERVER, port=REDIS_PORT)
api_url = 'http://list.didsoft.com/get?email=lincc@lamudatech.com&pass=sv7mmd&pid=http2000&https=yes&showcountry=no'
baidu_test_url = 'https://www.yahoo.com/'
big_pool_expire_seconds = 20 * 60
DUR = 300  # 同时测试的代理数量, 即线程数
MUL = 2  # 进程数

# logging基本配置
logging.basicConfig(
    # filename='jq-spider-api.log', filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


def write_txt(data):
    this_time = time.time()
    f = open(os.path.join('src/did_history', '%s.txt' % int(this_time)), 'w')
    f.write(data)
    f.close()


def run():
    global api_url
    before_ip = []
    while True:
        be = time.time()
        try:
            db = redis.Redis(connection_pool=redis_pool)

            # 从api请求代理并简单处理
            response = requests.get(api_url, timeout=60)
            # write_txt(response.text)

            now_ip = [i.split('#')[0] for i in response.text.split('\n')]
            ip_ports = [i for i in now_ip if i not in before_ip]
            before_ip = now_ip

            logging.info('get %s proxy' % len(ip_ports))

            # if proxy can visit baid.com, then go to big pool
            l = len(ip_ports)
            for i in range(0, l, DUR):
                multi_process(ip_ports[i: min(i + DUR, l)], db)
            print('*' * 66)
        except Exception as e:
            # traceback.print_exc()
            print(e)
            time.sleep(3 * 60)
        finally:
            used_time = time.time() - be
            print('total: %s s' % (used_time))
            sleep_time = 60 * 15 - used_time
            time.sleep(0 if sleep_time < 0 else sleep_time)


def multi_process(ip_ports, db):
    threads = []
    for ip_port in ip_ports:
        t = threading.Thread(target=test_proxy, args=(db, ip_port, baidu_test_url, 0))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()


if __name__ == '__main__':
    run()


