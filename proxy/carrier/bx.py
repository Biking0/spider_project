import requests,time,json,logging,urllib,random


def is_bx_ok(proxies, timeout_seconds=10):
    try:
        headers = {
            'Host': 'en.airbusan.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }
        res = requests.get('https://en.airbusan.com/content/individual/?', timeout=timeout_seconds, proxies=proxies, headers=headers)
        if res.status_code != 200:
            return False
        return True
    except:
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
        print(is_bx_ok(proxies))
        time.sleep(1)
