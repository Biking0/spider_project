# encoding:utf-8
import logging, traceback, time, sys
# import MySQLdb
import json
# pymysql.install_as_MySQLdb()
import requests, json, csv, os

BASE_URL = 'http://116.196.117.196/br/frals?'


# BASE_URL = 'http://test.jiaoan100.com/br_test/frals?'
# BASE_URL = 'http://localhost:9999/br/ib_frals?'


def get_port(path, name):
    data = read_csv(os.path.join(path, name + '.csv'))
    port = {}
    for i in data:
        if not len(i):
            continue
        port[i[0]] = 1
        port[i[1]] = 1
    print(port)
    print(len(port))
    return port


def read_csv(path):
    input_file = open(path)
    print(path)
    reader = csv.reader(input_file)
    data = list(reader)
    input_file.close()
    return data


def add_ports(path, name):
    ports = get_port(path, name)
    port_li = list(ports.keys())
    print(port_li)
    data = dict(
        data=port_li
    )
    url = 'http://dx.spider.jiaoan100.com/br/addports'
    status = requests.post(url, json.dumps(data), timeout=60).text
    print(status)


def update_ports(carrier, is_city=False):
    """
    :param carrier: 要更新的航司
    :param is_city: 是否是城市， 如果是城市对则传True
    :return:
    """
    params = {
        'carrier': carrier,
    }
    if is_city:
        params['city'] = 'true'
    res = requests.get(BASE_URL, params=params, timeout=30)
    datas = json.loads(res.text).get('data')
    datas.sort()
    output_file = open(os.path.join('updated_ports', '%s.csv' % carrier), 'wb')
    writer = csv.writer(output_file)
    for data in datas:
        dep, arr = data.split(',')
        writer.writerow([dep, arr])
    output_file.close()


def merge_to_one(main, *args):
    main = main + '.csv'
    total = set()
    for arg in args:
        data = read_csv(os.path.join('updated_ports', arg + '.csv'))
        print(len(data))
        data_str = [','.join(i) for i in data]
        total = total.union(set(data_str))
    data_list = []
    total = list(total)
    total.sort()
    print(total)
    output_file = open(os.path.join('updated_ports', main), 'w')
    writer = csv.writer(output_file)
    for item in total:
        data_list.append(item.split(','))
    print(len(data_list))
    writer.writerows(data_list)
    output_file.close()


if __name__ == '__main__':

    # update_ports('JT', False)  # get ports from web
    # add_ports('all_route', 'ZE')  # add new_ports to web

    update_ports('U2', False)  # get ports from web
    # add_ports('updated_ports', '4O')  # add new_ports to web

    # merge_to_one('DY', 'DY', 'DI', 'D8')  # merge multi to one

