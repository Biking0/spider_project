# coding=utf-8
# import sys
# sys.path.append('..')
import requests, json
import settings


def my_log(error):
    url = settings.LOG_URL
    data = {}
    requests.post(url, data=json.dumps(data))
    pass