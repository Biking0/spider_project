# coding=utf-8
import requests, json


def get_airport_city():
    api = 'http://dx.spider.jiaoan100.com/br/portcity?carrier=7C'
    response = requests.get(api)
    return json.loads(response.text).get('data')


if __name__ == '__main__':
    print(get_airport_city().get('JFK'))
