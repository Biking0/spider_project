# -*- coding: utf-8 -*-

import random
import json,time,requests,logging,traceback
from datetime import datetime,timedelta



def is_ww_ok(proxies,timeout_seconds=10):
    try:
        dt = (datetime.now() + timedelta(days=random.randint(3,10))).strftime('%Y-%m-%d')
        url = 'https://booking.wowair.com/api/midgardurCore/v5/bundles?'
        dep = 'AMS'
        arr = 'KEF'
        params = {
            'ApiKey': '',
            'Adults': '3',
            'Infants': '0',
            'Children': '0',
            'PromoCode': '',
            'Currency': 'USD',
            'Flights[0].origin': dep,
            'Flights[0].destination': arr,
            'Flights[0].departureDate': dt,
        }
        requests.get(url, params=params, timeout=timeout_seconds, proxies=proxies)
        return True
    except:

        return False

def _get_proxy():
    proxy=''
    try:
        url = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be'
        li = json.loads(requests.get(url,timeout=60).text)
        logging.info('Proxy Num:' + str(len(li)))
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
            'http':'http://%s'%ip_port,
            'https':'https://%s'%ip_port
        }
        print(is_ww_ok(proxies))
        time.sleep(5)