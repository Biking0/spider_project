import time
import logging
import threading

import gevent
import requests

import settings


def test_proxy(db, host_port, url, is_dx):
    proxies = {
        'http': 'http://%s' % host_port,
        'https': 'http://%s' % host_port
    }
    logging.info('test %s' % host_port)
    try:
        response = requests.get(url, proxies=proxies, timeout=3,
                                headers={"Connection": 'close'})
        if response.status_code != 200:
            logging.info('not pass baidu.com,passed')
            return
        logging.info('pass baidu, continue')
        db.lpush("proxy:big", host_port)
        db.set("proxy:ex:%s" % host_port, time.time())
        if not is_dx:
            db.incr("total:did", 1)

        pre = time.time()
        is_ok(db, proxies, host_port, is_dx)
        print('spend: %s' % (time.time() - pre))

    except Exception as e:
        # traceback.print_exc()
        print(e)
        logging.info('not pass baidu, next !!!')
        return


def is_ok(db, proxies, host_port, is_dx):

    def is_func_ok(func, carrier):
        if func(proxies=proxies):
            logging.info('pass %s, continue' % carrier)
            db.lpush("proxy:%s" % carrier, host_port)
            db.incr("total:%s" % carrier, 1)
            while db.llen("proxy:%s" % carrier) > 50:
                db.rpop('proxy:%s' % carrier)

    threads = []

    dic_fc = settings.CARRIER_FUNC
    for k, v in dic_fc.items():
        t = threading.Thread(target=is_func_ok, args=(v, k))
        t.start()
        threads.append(t)
        # threads.append(gevent.spawn(is_func_ok, v, k))

    if not is_dx:
        did_fc = settings.DID_FUNC
        for k, v in did_fc.items():
            t = threading.Thread(target=is_func_ok, args=(v, k))
            t.start()
            # t = gevent.spawn(is_func_ok, v, k)
            threads.append(t)
    for i in threads:
        i.join()
    # threading.joinall(threads)
    return


if __name__ == '__main__':
    proxies = {
        'http': 'http://121.205.254.113:37534',
        'https': 'http://121.205.254.113:37534',
    }
    import redis
    host_port = '121.205.254.113:37534'
    REDIS_SERVER = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_DB = 0
    redis_pool = redis.ConnectionPool(host=REDIS_SERVER, port=REDIS_PORT)
    db = redis.Redis(connection_pool=redis_pool)
    print(is_ok(db=db, proxies=proxies, host_port=host_port))
