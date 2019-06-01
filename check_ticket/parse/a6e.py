# encoding=utf-8
# check_ticket parse,6e
# by hyn
# 2019-01-23

from bs4 import BeautifulSoup
import time
import re


def data_parse(msg_dict):
    # 过滤邮件
    subject = msg_dict['Subject'].split(' ')
    if subject[0] != 'IndiGo':
        print('# 6e filter email')
        return

    ticket_no = subject[2]
    email = msg_dict['To'][1:-1]
    data = {
        # "name": '6E-CheckCard',
        # "dep_time": 0,
        # "ret_time": 0,
        # "flight_number": 0,
        "ticketNo": ticket_no,
        "addtime": time.time(),
        # "flight_type": 0,
        # 'gender': 0,
        "email": email,
        # 默认为2，不需验卡
        'check_card': 1
    }

    # print(data)
    return data

# data_parse(html_data)
