# encoding=utf-8
# check_ticket,wn
# by hyn
# 2018-12-19

from bs4 import BeautifulSoup
import time
import re
from utils import u2_year


def data_parse(msg_dict):
    # 过滤邮件
    subject = msg_dict['Subject'].split(' ')
    if subject[-1] != 'confirmed.':
        print('# wn filter email')
        return

    soup = BeautifulSoup(msg_dict['text'], "lxml")

    flight_info = soup('table')[17]
    ticket_no = flight_info('p')[0].text.strip().split(' ')[-1]
    print(ticket_no)
    flight_info = soup('table')[17]
    name_info = flight_info('table')[3]('tr')

    name_list = []
    for i in name_info:
        name_list.append(i('td')[1]('p')[0].text.strip())

    # 处理乘客名字
    name = ''
    for name_str in name_list:
        name_str_list = name_str.split('\xa0')
        if name == '':
            for i in name_str_list[:-1]:
                name = name + i
            name = name_str_list[-1] + '/' + name
        else:
            temp_name = ''
            for i in name_str_list[:-1]:
                temp_name = temp_name + i
            name = name + ',' + name_str_list[-1] + '/' + temp_name

    time_info = soup('table')[23]('p')
    flight_number = 'WN' + time_info[5].text.strip().split(' ')[-1].lstrip('0')

    # Sunday, 12/30/201801:25PM
    dep_time = time.mktime(
        time.strptime(time_info[1].text.strip() + time_info[7].text.strip().split(' ')[-1], '%A, %m/%d/%Y%H:%M%p'))

    flight_type = 1
    ret_time = 0
    # 返程
    if len(soup('table')) > 68:
        flight_type = 2
        flight_info = soup('table')[35]
        flight_number = flight_number + ',WN' + flight_info('p')[1].text.strip().split(' ')[-1].lstrip('0')
        ret_time = time.mktime(
            time.strptime(soup('table')[32].text.strip() + soup('table')[35]('p')[3].text.strip().split(' ')[-1],
                          '%A, %m/%d/%Y%H:%M%p'))
    name = name.upper()
    data = {
        "name": name,
        "dep_time": dep_time,
        "ret_time": ret_time,
        "flight_number": flight_number,
        "ticketNo": ticket_no,
        "addtime": time.time(),
        "flight_type": flight_type,
        "email": msg_dict['To'][1:-1]
    }
    # print(data)
    return data
