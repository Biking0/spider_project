import requests,time,json,logging, traceback, random, time, random
from urllib import parse
from datetime import datetime, timedelta
from random import randint


def is_ls_ok(proxies, timeout_seconds=10):
    try:
        timeout_seconds = timeout_seconds
        _date = (datetime.now() + timedelta(days=randint(3, 10))).strftime('%Y-%m-%d')
        url = 'https://www.jet2.com/en/cheap-flights/Belfast/Antalya?from={0}adults=5&children&infants=0&preselect=true'.format(_date)

        headers = {
            'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'Cache-Control': "no-cache",
            'referer': 'https://www.jet2.com/',
            'upgrade-insecure-requests': "1",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36"
        }
        requests.get(url, headers=headers, timeout=timeout_seconds, proxies=proxies)
        # print(res.status_code)
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
        print(is_ls_ok(proxies))
        time.sleep(5)
