# encoding:utf-8
import requests,time,json,logging,urllib, traceback
import random

def is_dd_ok(proxies, timeout_seconds=10):
    try:

        data = {
            "ClientVersion": "6.0.2",
            "UserName": "NOKIPHOAPP",
            "Password": "n03@!hOH3zOieAPq1",
            "GetAvailabilityDetail": {
                "Infant": 0,
                "DepartureAirport": "DMK",
                "ArrivalAirport": "UTH",
                "Child": 0,
                "Currency": "THB",
                "RoundTripFlag": "0",
                "Adult": 3,
                "AgencyCode": "",
                "ReturnDate": "",
                "BoardDate": "2018/05/01",
                "PromotionCode": "",
            },
            "SessionID": "B157CA09A460459C95605B94C3925E80:020518173906"
        }

        header = {
            'Host': 'api.nokair.com',
            'Content-Type': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'NokAir/10 CFNetwork/811.5.4 Darwin/16.7.0',
            'Accept-Language': 'en-us',
            'Accept': '*/*',
        }
        res = requests.post('https://api.nokair.com/services/services.svc/REST/GetAvailability', data=json.dumps(data), headers=header, proxies=proxies, timeout=timeout_seconds)
        res_dict = json.loads(res.text)
        if res.status_code != 200 or int(res_dict.get('Code')):
            return False
        return True
    except:
        # traceback.print_exc()
        return False

# 测试用的

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
        print(proxy)
        return proxy or ''

if __name__ == '__main__':
    while True:
        ip_port = _get_proxy()
        proxies = {
            'http': 'http://%s' % ip_port,
            'https': 'https://%s' % ip_port
        }
        print(is_dd_ok(proxies))
        time.sleep(1)
