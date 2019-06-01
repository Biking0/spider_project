import requests,time,json,logging,urllib

def is_be_ok(proxies, timeout_seconds=5):
    try:
        res = requests.get(
            'https://www.flybe.com/api/fares/day/new/ALC/DSA?depart=ALC&arr=DSA&departing=2018-02-13&' +
            'returning=&promo-code=&adults=1&teens=0&children=0&infants=0', proxies=proxies, timeout=timeout_seconds)
        if res.status_code != 200:
            return False
        return True
    except:
        return False


if __name__ == '__main__':
    proxies = {
        'http': 'http://121.205.254.113:37534',
        'https': 'http://121.205.254.113:37534',
    }
    print(is_be_ok(proxies=proxies, timeout_seconds=20))
