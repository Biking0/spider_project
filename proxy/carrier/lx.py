import requests,time,json,logging,urllib, traceback, random

def is_lx_ok(proxies, timeout_seconds=10):
    try:
        res = requests.get('https://www.swiss.com/us/en/Book/Outbound/AGP-ZRH/from-2018-04-10/adults-1/children-0/infants-0/class-economy', proxies=proxies, timeout=timeout_seconds)
        # print(res.text)
        return True
    except:
        return False




def _get_proxy():
    proxy=''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=lx', time).text)
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
        print(is_lx_ok(proxies))
        time.sleep(5)


