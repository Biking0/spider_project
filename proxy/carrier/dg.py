import requests,time,json,logging, traceback, random, time, random
from urllib import parse
from datetime import datetime, timedelta
from random import randint


def is_dg_ok(proxies, timeout_seconds=10):
    try:
        url = 'https://beta.cebupacificair.com/Mobile/Flight/Select?'
        _date = (datetime.now() + timedelta(days=randint(3, 10))).strftime('%Y-%m-%d')
        params = parse.urlencode(dict(
            o1='MNL', d1='ICN', o2='', dd1=_date, ADT=1,
            CHD=0, INF=0, inl=0, pos='cebu.ph', culture=''
        ))
        res = requests.get(url, params=params, timeout=timeout_seconds, proxies=proxies)
        # print(res.text)
        if res.status_code == 200:
            if 'Are you human?' not in res.text:
                return True
        return False
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
        print(is_dg_ok(proxies))
        time.sleep(5)
