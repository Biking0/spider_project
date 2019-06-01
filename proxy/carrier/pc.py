# -*- coding: utf-8 -*-

import random
import json,time,requests,logging,traceback
from datetime import datetime,timedelta
from random import randint


def is_pc_ok(proxies,timeout_seconds=10):
    try:
        url = 'https://mw.flypgs.com/pegasus/availability'
        headers = {
            'accept-language': "en",
            'x-platform': "android",
            'x-version': "2.4.0",
            'x-system-version': "4.4.2",
            'x-device-id': "9a541b5e362a3356",
            'content-type': "application/json; charset=UTF-8",
            'host': "mw.flypgs.com",
            'accept-encoding': "gzip",
            'user-agent': "okhttp/3.9.0",
            'connection': "keep-alive",
        }
        seat, dep, to = 3, 'SAW', 'JED'
        _date = (datetime.now() + timedelta(days=randint(3, 10))).strftime('%Y-%m-%d')
        # print(_date)
        payload = {
                    "flightSearchList": [{
                        "arrivalPort": to,
                        "departurePort": dep,
                        "departureDate": _date
                    }],
                    "adultCount": seat,
                    "childCount": 0,
                    "infantCount": 0,
                    "soldierCount": 0,
                    "currency": "TL",
                    "operationCode": "TK",
                    "ffRedemption": False,
                    "openFlightSearch": False,
                    "personnelFlightSearch": False,
                    "dateOption": 1
                }

        res = requests.post(url, headers=headers, data=json.dumps(payload), timeout=timeout_seconds, proxies=proxies)
        # print(res.text)
        return True
    except:
        return False


def _get_proxy():
    proxy=''
    try:
        url = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=pc'
        li = json.loads(requests.get(url, timeout=60).text)
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
        print(is_pc_ok(proxies))
        time.sleep(5)
