import json

import requests

import utils


def get_data():
    url = "https://cn.airbusan.com/web/bookingApi/flightsAvail"
    payload = dict(
        bookingCategory='Individual',
        focYn='N',
        tripType='OW',
        depCity1='PUS',
        arrCity1='NRT',
        depDate1='2018-12-27',
        paxCountCorp=0,
        paxCountAd=1,
        paxCountCh=0,
        paxCountIn=0
    )
    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'origin': "https://cn.airbusan.com",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'referer': "https://cn.airbusan.com/web/individual/booking/flightsAvail",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        'cache-control': "no-cache",
        }
    response = requests.request("POST", url, data=payload, headers=headers, verify=False)
    print(response.text)


def get_route():
    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'origin': "https://cn.airbusan.com",
        'x-requested-with': "XMLHttpRequest",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.80 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded",
        'referer': "https://cn.airbusan.com/content/individual/?",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        'cache-control': "no-cache",
    }
    url = ' https://cn.airbusan.com/web/bookingApi/bookingCity'
    res = requests.get(url, headers=headers, verify=False)
    data = json.loads(res.text)
    index = ['domBlockCity', 'intBlockCity', 'listRouteYearAvail']
    routes = set()
    for li in index:
        item_li = data.get(li)
        for item in item_li:
            dep = item.get('depCity')
            arrs = item.get('arrCity').split(',')
            routes.update(set(['%s_%s' % (dep, arr)for arr in arrs]))
    routes = [i.split('_') for i in routes]
    utils.write_csv('all_route', 'BX', routes)


if __name__ == '__main__':
    get_data()