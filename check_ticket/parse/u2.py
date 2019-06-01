# encoding=utf-8
# check_ticket,parse
# by hyn
# 2018-12-12

from bs4 import BeautifulSoup
import time
import re
from utils import u2_year


def data_parse(msg_dict):
    # 过滤邮件
    subject = msg_dict['Subject'].split(' ')
    if subject[0] != 'easyJet':
        print('# u2 filter email')
        return

    sex = {
        'Mr': 'M',
        'Mrs': 'F',
        'Miss': 'F',
        'Ms': 'F',
        'child': 'C'
    }

    soup = BeautifulSoup(msg_dict['text'], "lxml")
    p1 = re.compile(r'[(](.*?)[)]', re.S)

    error_data = {'error_data': {}}
    try:
        ticket_no = re.findall(p1, soup('title')[0].text.strip())[0]

        flight_info = soup('table')[8]
        flight_number = 'U2' + re.findall(r'[0-9]+|[a-z]+', flight_info('td')[4].string.strip())[0]
        dep_time_str = flight_info('table')[0]('table')[1]('td')[1].text

    except Exception as e:
        # 非标准确认邮件
        error_info = 'ticket_number error, not standard mail for u2'
        error_data['error_data']['Subject'] = msg_dict['Subject']
        error_data['error_data']['error_info'] = error_info
        error_data['error_data']['exception'] = e
        print(error_info)
        # return error_data

        # 该出票编码已在其它邮件中解析
        return

    try:
        dep_time = time.strptime(dep_time_str, '%a %d %b %H:%M')
    except Exception as e:
        # 非英文邮件，时间转换出错
        error_info = 'time covert error, not english language'
        error_data['error_data']['Subject'] = msg_dict['Subject']
        error_data['error_data']['error_info'] = error_info
        error_data['error_data']['exception'] = e
        print(error_info)
        # return error_data
        # 该出票编码已在其它邮件中解析
        return

    # 当邮件月份小于当前月份，取当年月份加1
    year = u2_year(dep_time)
    dep_time = time.strptime(dep_time_str + year, '%a %d %b %H:%M%Y')
    dep_time = time.mktime(dep_time)

    # 判断人数
    counts = flight_info.find_all('td')
    # 存储名字，逗号隔开
    name = ''
    gender = ''
    for count in counts[17:]:
        name_list = count.text.strip().split(' ')

        # 寻找人名
        if name_list[0][0] == 'M' or name_list[0] == 'child':
            if name == '':
                for i in name_list[1:-1]:
                    name = name + i
                name = name_list[-1] + '/' + name
                gender = sex.get(name_list[0])
            else:
                temp_name = ''
                for i in name_list[1:-1]:
                    temp_name = temp_name + i
                name = name + ',' + name_list[-1] + '/' + temp_name
                gender = gender + ',' + sex.get(name_list[0])

    ret_time = 0
    flight_type = 1

    # 返程
    if len(soup('table')) > 55:
        flight_info = soup('table')[16]
        flight_number = flight_number + ',' + 'U2' + re.findall(r'[0-9]+|[a-z]+', flight_info('td')[0].text.strip())[0]

        ret_time_str = soup('table')[17]('td')[1].text
        ret_time = time.strptime(soup('table')[17]('td')[1].text, '%a %d %b %H:%M')

        year = u2_year(ret_time)
        ret_time = time.strptime(ret_time_str + year, '%a %d %b %H:%M%Y')
        ret_time = time.mktime(ret_time)
        flight_type = 2

    email = msg_dict['To'][1:-1]

    if name == '':
        print('# name is null')
        print(ticket_no)
        return
    data = {
        "name": name,
        "dep_time": dep_time,
        "ret_time": ret_time,
        "flight_number": flight_number,
        "ticketNo": ticket_no,
        "addtime": time.time(),
        "flight_type": flight_type,
        'gender': gender,
        "email": email
    }

    # print(data)
    return data
