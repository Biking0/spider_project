import requests,time,json,logging, traceback, random, time, random
from urllib import parse
from datetime import datetime, timedelta
from random import randint


def is_as_ok(proxies, timeout_seconds=10):
    try:
        url = 'https://m.alaskaair.com/shopping/flights/'
        headers = {
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'origin': "https://m.alaskaair.com",
            'referer': "https://m.alaskaair.com/shopping/flights",
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        }
        res = requests.get(url, headers=headers, timeout=timeout_seconds, proxies=proxies)
        if res.status_code == 403:
            return False
        return True
    except:
        # traceback.print_exc()
        return False

def _get_proxy():
    proxy=''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be', time).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''
        print(proxy)
    except:
        traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        return proxy or ''

if __name__ == '__main__':
    while True:
        ip_port = _get_proxy()
        proxies = {
            'http': 'http://%s' % ip_port,
            'https': 'http://%s' % ip_port
        }
        print(is_as_ok(proxies))
        time.sleep(5)
