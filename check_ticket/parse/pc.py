# encoding=utf-8
# check_ticket,parse
# by hyn
# 2018-12-18

from bs4 import BeautifulSoup
import time
import re


def data_parse(msg_dict):
    # 过滤邮件
    subject = msg_dict['Subject'].split(' ')
    if subject[0] != 'Online':
        print('# pc filter email')
        return

    sex = {
        'Male': 'M',
        'Female': 'F',
        'Child': 'C'
    }

    soup = BeautifulSoup(msg_dict['text'], "lxml")
    ticket_no = soup('p')[0].text.split(' ')[-1]
    flight_info = soup('table')[9]
    temp_flight_number = re.split('(\d+|\+|-|\*|/)', flight_info('td')[5].text.split(' ')[2])

    flight_number = temp_flight_number[0] + temp_flight_number[1]
    # 18/12/201821:10
    dep_time_str = str(flight_info('td')[10].text.strip().split(' ')[-1] + flight_info('td')[17].text)
    dep_time = time.mktime(time.strptime(dep_time_str, '%d/%m/%Y%H:%M'))

    # 获取乘客名字
    name_info = soup('table')[14]('tr')
    name = ''
    gender = ''
    for i in name_info[1:]:
        name_list = i('td')[0].text.replace(' ', '').replace('\n', ' ').replace('\r', '').split(' ')
        sex_info = i('td')[1].text.replace(' ', '').replace('\n', ' ').replace('\r', '')
        if not name:
            for j in name_list[:-1]:
                name = name + j
            name = name_list[-1] + '/' + name
            gender = sex.get(sex_info)
        else:
            temp_name = ''
            for i in name_list[:-1]:
                temp_name = temp_name + i
            name = name + ',' + name_list[-1] + '/' + temp_name
            gender = gender + ',' + sex.get(sex_info)

    ret_time = 0
    flight_type = 1

    # 返程
    if len(soup('table')) > 33:
        flight_info = soup('table')[17]
        temp_flight_number = re.split('(\d+|\+|-|\*|/)', flight_info('td')[4].text.split(' ')[2])
        flight_number = flight_number + ',' + temp_flight_number[0] + temp_flight_number[1]
        # 18/12/201821:10
        ret_time_str = str(flight_info('td')[9].text.strip().split(' ')[-1] + flight_info('td')[16].text)
        ret_time = time.mktime(time.strptime(ret_time_str, '%d/%m/%Y%H:%M'))
        flight_type = 2

    email = msg_dict['To'][1:-1]

    data = {
        "name": name,
        "dep_time": dep_time,
        "ret_time": ret_time,
        "flight_number": flight_number,
        "ticketNo": ticket_no,
        "addtime": time.time(),
        "flight_type": flight_type,
        'gender': gender,
        "email": email,
        # "checked": 1
    }

    # print(data)
    return data

# data_parse(html_data)
