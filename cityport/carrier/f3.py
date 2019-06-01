# encoding:utf-8
import re
import os
import csv

import requests


def get_session():
    url = "https://book.flyadeal.com/api/session"

    headers = {
        'accept': "application/json, text/plain, */*",
        'origin': "https://book.flyadeal.com",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/69.0.3497.100 Safari/537.36",
        'referer': "https://book.flyadeal.com/",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        'cache-control': "no-cache",
        'postman-token': "bf36a116-311a-2474-6ce8-130be8e3665d"
    }

    response = requests.request("POST", url, headers=headers, verify=False)

    token = response.headers.get("x-session-token")
    print(token)
    return token


def get_data(token):
    url = "https://book.flyadeal.com/api/flights"

    querystring = {"availabilityRequests[0].departureStation": "DMM", "availabilityRequests[0].arrivalStation": "JED",
                   "availabilityRequests[0].beginDate": "2018-11-07", "availabilityRequests[0].endDate": "2018-11-07",
                   "availabilityRequests[0].paxTypeCounts[0].paxTypeCode": "ADT",
                   "availabilityRequests[0].paxTypeCounts[0].paxCount": "1",
                   "availabilityRequests[0].currencyCode": "SAR", "availabilityRequests[0].paxResidentCountry": "SA",
                   "availabilityRequests[0].promotionCode": ""}

    headers = {
        'accept': "application/json, text/plain, */*",
        'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, "
                      "like Gecko) Chrome/69.0.3497.100 Safari/537.36",
        'referer': "https://book.flyadeal.com/",
        'accept-encoding': "gzip, deflate, br",
        'accept-language': "zh-CN,zh;q=0.9",
        'cache-control': "no-cache",
        'postman-token': "32187cc7-551c-c7bc-b183-f4421daec695",
        'x-session-token': token
    }

    response = requests.request("GET", url, headers=headers, params=querystring, verify=False)
    print(response.text)


def simple_spider():
    token = get_session()
    get_data(token)


def get_routines():

    # 可获取routines数据
    # url = 'https://www.flyadeal.com/en/'
    # headers = {
    #     'upgrade-insecure-requests': "1",
    #     'user-agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) "
    #                   "Chrome/69.0.3497.100 Safari/537.36",
    #     'accept': "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    #     'accept-encoding': "gzip, deflate, br",
    #     'accept-language': "zh-CN,zh;q=0.9",
    #     'cache-control': "no-cache",
    #     'postman-token': "186848c2-7085-eb21-8852-933ed85e2706"
    # }
    # res = requests.request("GET", url, headers=headers, verify=False)
    # data = res.text
    # market_str = re.search('flyadealmarket = (*);', data)

    markets = [
        {
            "key": "AHB",
            "value": [
                "JED",
                "RUH"
            ]
        },
        {
            "key": "JED",
            "value": [
                "AHB",
                "DMM",
                "ELQ",
                "GIZ",
                "RUH",
                "TUU"
            ]
        },
        {
            "key": "RUH",
            "value": [
                "AHB",
                "GIZ",
                "JED",
                "MED",
                "TUU"
            ]
        },
        {
            "key": "DMM",
            "value": [
                "JED"
            ]
        },
        {
            "key": "ELQ",
            "value": [
                "JED"
            ]
        },
        {
            "key": "GIZ",
            "value": [
                "JED",
                "RUH"
            ]
        },
        {
            "key": "TUU",
            "value": [
                "JED",
                "RUH"
            ]
        },
        {
            "key": "MED",
            "value": [
                "RUH"
            ]
        }
    ]
    routine = []
    for market in markets:
        dep = market.get('key')
        value = market.get('value')
        for arr in value:
            routine.append([dep, arr])

    output_file = open(os.path.join('../all_route', 'F3.csv'), 'w')
    writer = csv.writer(output_file)
    writer.writerows(routine)
    output_file.close()


if __name__ == '__main__':
    simple_spider()
    # get_routines()
