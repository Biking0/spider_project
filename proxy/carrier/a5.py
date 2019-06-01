import requests, time, json, logging, urllib, random
import traceback


def is_a5_ok(proxies, timeout_seconds=2):
    try:
        res = requests.get('https://www.hop.com/', proxies=proxies, timeout=timeout_seconds)
        if res.status_code != 200 and res.status_code != 403:
            return False
        return True
    except Exception as e:
        print(e)
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
        print(is_a5_ok(proxies))
        time.sleep(1)
