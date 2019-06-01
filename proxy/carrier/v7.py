import requests,time,json,logging, traceback, random, time, random
from urllib import parse
from datetime import datetime, timedelta
from random import randint


def is_v7_ok(proxies, timeout_seconds=10):
    try:
        dt = (datetime.now() + timedelta(days=randint(3, 10))).strftime('%Y-%m-%d')
        url = 'https://booking.volotea.com/Search.aspx?'
        dep = 'RHO'
        arr = 'PMO'
        params = {
            'culture': 'en-GB',
            'bookingtype': 'flight',
            'from': dep,
            'to': arr,
            'departuredate': dt,
            'returnDate': '2018-07-23',
            'adults': 1,
            'children': 0,
            'infants': 0,
            'showNewSearch': False,
            'triptype': 'OneWay',
            'residentFamilyType': '',
            'useCookie': False,
            'currency': 'EUR',
        }
        requests.get(url, params=params, timeout=timeout_seconds, proxies=proxies)
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
        print(is_v7_ok(proxies))
        time.sleep(5)
