import requests,time,json,logging, traceback, random, time, random
from urllib import parse
from datetime import datetime, timedelta
from random import randint
from bs4 import BeautifulSoup


def is_tw_ok(proxies, timeout_seconds=10):
    res = None
    try:
        url = 'https://www.twayair.com/booking/availabilityList.do'
        headers = {
            'Host': 'www.twayair.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://www.twayair.com/main.do?_langCode=EN',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:60.0) Gecko/20100101 Firefox/60.0',
            
		}
        res = requests.get(url, headers=headers, timeout=timeout_seconds, proxies=proxies)
        soup = BeautifulSoup(res.text, 'lxml')
        searchAvailId = soup.select_one('input[name="searchAvailId"]')['value']
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
        # ip_port = ''
        proxies = {
            'http': 'http://%s' % ip_port,
            'https': 'http://%s' % ip_port
        }
        print(is_tw_ok(proxies))
        time.sleep(5)
