# encoding:utf-8
import re
import json

import requests

import utils


def get_data():
    url = "https://mapi.vietjetair.com/apiios/get-flight2.php"

    headers = {
        'accept': "application/json, text/javascript, */*; q=0.01",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        'origin': "https://m.vietjetair.com",
        'referer': "https://m.vietjetair.com/",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
        'Cache-Control': "no-cache"
    }

    data = {
        'OutboundDate': _day,
        'DaysBefore': '0',
        'DaysAfter': '0',
        'AdultCount': '9',
        'ChildCount': '0',
        'InfantCount': '0',
        'DepartureAirportCode': FROM,
        'ArrivalAirportCode': TO,
        'CurrencyCode': 'VND',
        'PromoCode': ''
    }

    response = requests.post(url, data=json.dumps(data), headers=headers, verify=False)

    # token = response.headers.get("x-session-token")
    print(response.text)


def simple_spider():
    get_data()


def get_routes():
    url = 'https://www.vietjetair.com/AirportList.aspx?lang=zh-CN'
    res = requests.get(url, timeout=30)
    data = json.loads(res.text)
    pairs = data.get('Pair')
    routes = []
    for pair in pairs:
        dep = pair.get('DepartureAirport').get('Code')
        arrs = pair.get('ArrivalAirports').get('Airport')
        for port in arrs:
            arr = port.get('Code')
            routes.append([dep, arr])
    utils.write_csv('all_route', 'VJ', routes)


if __name__ == '__main__':
    # simple_spider()
    get_routes()
