import requests,time,json,logging,urllib, random



def is_sl_ok(proxies, timeout_seconds=10):
    try:
        headers = {
            'Host': 'mobile.lionairthai.com',
            'Origin': 'http://mobile.lionairthai.com',
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept-Encoding': 'gzip, deflate',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60',
            'Referer': 'http://mobile.lionairthai.com/var/containers/Bundle/Application/DAA972CB-192A-4655-ABD7-8B1E0E3B8FC5/ThaiLionAir.app/www/index.html',
            'Accept-Language': 'en-us',
            'Accept': 'application/json, text/plain, */*',
        }
        data = {
            "sd": {
                "Adults": 1,
                "AirlineCode": "",
                "ArrivalCity": "DMK",
                "ArrivalCityName": None,
                "BookingClass": None,
                "CabinClass": 0,
                "ChildAge": [],
                "Children": 0,
                "CustomerId": 0,
                "CustomerType": 0,
                "CustomerUserId": 207,
                "DepartureCity": "URT",
                "DepartureCityName": None,
                "DepartureDate": "/Date(0)/",
                "DepartureDateGap": 0,
                "DirectFlightsOnly": False,
                "Infants": 0,
                "IsPackageUpsell": False,
                "JourneyType": 1,
                "PreferredCurrency": "THB",
                "ReturnDate": "/Date(-2208988800000)/",
                "ReturnDateGap": 0,
                "SearchOption": 1
            },
            "fsc": "0"
        }
        url = 'https://mobile.lionairthai.com/GQWCF_FlightEngine/GQDPMobileBookingService.svc/SearchAirlineFlights'
        res = requests.post(url, data=json.dumps(data), headers=headers, proxies=proxies, timeout=timeout_seconds)
        # if res.status_code == 400:
        #     return True
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
        print(is_sl_ok(proxies))
        time.sleep(5)
