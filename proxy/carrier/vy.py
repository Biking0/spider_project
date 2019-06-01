import requests,time,json,logging,urllib, traceback, random

def is_vy_ok(proxies, timeout_seconds=10):
    try:
        headers = {
            'Host': 'apimobile.vueling.com',
            'Content-Type': 'application/json',
            'cookie': '',
            'Accept': '*/*',
            'Accept-Language': 'en-us',
            'User-Agent': 'Vueling/881 CFNetwork/811.5.4 Darwin/16.7.0',
        }
        data = {
            "DiscountType": 0,
            "AppVersion": "881",
            "DeviceModel": "iPhone 6P",
            "CurrencyCode": "EUR",
            "TimeZone": 8,
            "Language": "EN",
            "AirportDateTimeList": [{
                "MarketDateDeparture": "2018-05-06T00:00:00",
                "DepartureStation": "LGW",
                "ArrivalStation": "GOA"
            }],
            "Xid": "",
            "InstallationID": "C1A27204-AE51-408A-89B7-655B2FC6F384",
            "Paxs": [{
                "Paxtype": "ADT",
                "Quantity": 1
            }, {
                "Paxtype": "CHD",
                "Quantity": 0
            }, {
                "Paxtype": "INF",
                "Quantity": 0
            }],
            "OsVersion": "10.3.3",
            "Currency": "EUR",
            "DeviceType": "IOS",
        }
        url = 'https://apimobile.vueling.com/Vueling.Mobile.AvailabilityService.WebAPI/api/AvailabilityController/DoAirPriceSB'
        res = requests.post(url, data=json.dumps(data), headers=headers, timeout=timeout_seconds, proxies=proxies)
        if res.status_code == 200:
            return True
        return False
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
        print(is_vy_ok(proxies))
        time.sleep(5)
