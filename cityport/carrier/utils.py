import os
import csv
import json
import random
import logging
import traceback

import requests


def write_csv(dic, name, data):
    """
    将航线数据排序写入对应文件夹的对应名字下
    :param dic: 目录， 暂时包括"all_route"和"updated_route"
    :param name: 文件名，一般是大写的carrier,
    :param data: 还未排序的航线， 格式： [['dep', 'arr'], ....]
    :return: None
    """
    data.sort()
    name = name.upper()
    output_file = open(os.path.join('../%s' % dic, '%s.csv' % name), 'w')
    writer = csv.writer(output_file)
    writer.writerows(data)
    output_file.close()


def get_proxy(carrier='BE'):
    proxy = ''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=%s' % carrier, timeout=10).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''
        print(proxy)
    except:
        traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        proxies = {
            'http': 'http://%s' % proxy,
            'https': 'http://%s' % proxy
        }
        return proxies


if __name__ == '__main__':
    print(get_proxy('VY'))
