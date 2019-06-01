import requests,time,json,logging, traceback, random, time, random
from urllib import parse
from datetime import datetime, timedelta
from random import randint


def is_mm_ok(proxies, timeout_seconds=10):

    _date = (datetime.now() + timedelta(days=randint(3, 10))).strftime('%Y/%m/%d')

    data = {
        "flight_search_parameter[0][departure_date]": _date,
        "flight_search_parameter[0][departure_airport_code]": "PUS",
        "flight_search_parameter[0][arrival_airport_code]": "KIX",
        "flight_search_parameter[0][is_return]": False,
        "flight_search_parameter[0][return_date]": "",
        "adult_count": 1,
        "child_count": 0,
        "infant_count": 0,
        "r": "static_search",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-CN,zh;q=0.9",
        "Cache-Control": "max-age=0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "booking.flypeach.com",
        "Origin": "https://booking.flypeach.com",
        "Referer": "https://www.flypeach.com/pc/en",
        "Upgrade-Insecure-Requests": "1",
    }
    url_cn = 'https://booking.flypeach.com/en'
    url = 'https://booking.flypeach.com/en'
    # se.get(url, headers=headers_first, timeout=10, allow_redirects=False, verify=False)
    # response = se.post(url, data=json.dumps(data_cn), headers=headers_en, timeout=5, allow_redirects=False, verify=False)
    try:
        response = requests.post(url_cn, data=data, proxies=proxies, headers=headers, timeout=timeout_seconds, allow_redirects=False)
        cookie = response.cookies.get('reqid')
        if not cookie:
            return False
        return True
    except:
        # traceback.print_exc()
        return False

def _get_proxy():
    proxy=''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be', timeout=10).text)
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
        print(is_mm_ok(proxies))
        time.sleep(5)
