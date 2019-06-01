# encoding=utf-8
# flyadeal,F3
# by hyn
# 2018-12-26

import requests, time, json, logging, random
import traceback


def is_f3_ok(proxies, timeout=10):
    invalid_status = [401, 403]
    try:
        get_token_url = "https://book.flyadeal.com/api/session"
        headers = {
            'accept': "application/json, text/plain, */*",
            'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/69.0.3497.100 Safari/537.36",
            'referer': "https://book.flyadeal.com/",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cache-control': "no-cache",
        }
        res = requests.post(get_token_url, proxies=proxies, headers=headers, timeout=timeout)
        if res.status_code in invalid_status:
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
        print(is_f3_ok(proxies))
        time.sleep(1)

