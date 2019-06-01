# encoding=utf-8
# spirit,NK
# by hyn
# 2019-01-11

import requests, time, json, logging, random
import traceback


def is_nk_ok(proxies, timeout=10):
    try:
        get_session_url = "https://www.spirit.com/"
        res = requests.get(get_session_url, proxies=proxies, timeout=15)
        # res = requests.post(get_token_url, proxies=proxies, headers=headers, timeout=timeout)
        if res.status_code is not 200:
            return False
        return True
    except Exception as e:
        # print(e)
        return False


def _get_proxy():
    proxy = ''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be', time).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''
        print(proxy)
    except Exception as e:
        print(e)
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
        print(is_nk_ok(proxies))
        time.sleep(1)
