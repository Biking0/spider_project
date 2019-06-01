import os
import csv
import json
import time
import random
import logging
import traceback

import requests
from jsonpath import jsonpath

proxies = None


def get_port():
    url = 'https://www.flybe.com/gw/data/airports'
    global proxies
    while True:
        try:
            res = requests.get(url, proxies=proxies, timeout=30)
            data = json.loads(res.text)
            break
        except Exception as e:
            print(e)
            proxies = _get_proxy()
            time.sleep(2)
    ports = data.get('originAirports')
    return ports.keys()


def get_direct(ports):
    base_url = 'https://www.flybe.com/gw/data/citypairs/'
    global proxies
    route_data = []
    for dep in list(ports):
        url = base_url + dep
        while True:
            try:
                res = requests.get(url, proxies=proxies, timeout=30)
                data = json.loads(res.text)
                arrs = data.get('destinationAirports')
                items = arrs.items()
                for arr, v in items:
                    indirect_only = jsonpath(v, '$..indirectOnly')[0]
                    if indirect_only == 'false':
                        route_data.append([dep, arr])
                break
            except Exception as e:
                print(e)
                proxies = _get_proxy()
                time.sleep(2)
    return route_data


def write_csv(data, name):
    print(data)
    output_file = open(os.path.join('../all_route', name + '.csv'), 'w')
    writer = csv.writer(output_file)
    data.sort()
    writer.writerows(data)
    output_file.close()


def _get_proxy():
    proxy=''
    try:
        li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=be', timeout=30).text)
        logging.info('Proxy Num: ' + str(len(li)))
        logging.info(str(li))
        proxy = random.choice(li) or ''
        print(proxy)
        proxies = {
            'http': 'http://%s' % proxy,
            'https': 'http://%s' % proxy
        }
    except:
        traceback.print_exc()
        logging.info('get proxy error....')
    finally:
        return proxies or ''


if __name__ == '__main__':
    proxies = _get_proxy()
    ports = get_port()
    route_data = get_direct(ports)
    write_csv(route_data, 'BE')
    # print(get_port())

