# encoding=utf-8
# kn
# by hyn
# 2019-02-19

import requests, time, json, logging, random
import traceback
from datetime import datetime, timedelta
from fake_useragent import UserAgent


def is_kn_ok(proxies, timeout=10):
    try:
        url = "http://wx.flycua.com/wechat/pip/book/flightSearch.json"

        ua = UserAgent()
        headers = {
            'Host': "wx.flycua.com",
            'Origin': "http://wx.flycua.com",
            'User-Agent': ua.random,
            'isWechat': "H5",
            'Content-Type': "application/json;charset=UTF-8",
            'Accept': "application/json, text/plain, */*",
            'Cookie': "JSESSIONID=7DB644CF0C5608A8198719E96B1AF8B9",
        }
        date = datetime.now() + timedelta(days=10)
        date = date.strftime('%Y-%m-%d')

        post_data = {
            "tripType": "OW",
            "orgCode": "FUK",
            "dstCode": "YNT",
            "takeoffdate1": date,
        }

        print(post_data)
        # proxies = {'http': 'http://127.0.0.1:8888'}
        res = requests.request("POST", url, proxies=proxies, data=json.dumps(post_data), headers=headers, timeout=15)

        # ip deny
        try:
            json_dict = json.loads(res.text.encode('utf-8'))
        except:
            logging.info('# ip deny')
            return False

        # 登陆
        if json_dict.get('commonRes').get('code') == 'PREVENT0001':
            logging.info('# need login')
            return False

        # if not json_dict.get('commonRes').get('isOk'):
        #     return False
        print(json_dict)
        return True
    except Exception as e:
        print(e)
        return False


def _get_proxy():
    proxy = ''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be', time).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''
        print(proxy)
    except Exception as e:
        print(e)
        traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        return proxy or ''


if __name__ == '__main__':
    while True:
        ip_port = _get_proxy()
        proxies = {
            'http': 'http://%s' % ip_port,
            # 'https': 'http://%s' % ip_port
        }
        print(is_kn_ok(proxies))
        time.sleep(1)
