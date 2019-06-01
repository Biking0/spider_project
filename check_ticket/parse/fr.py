# encoding=utf-8
# check_ticket,parse
# by hyn
# 2018-12-15


from bs4 import BeautifulSoup
import time


def data_parse(msg_dict):
    # print(msg_dict)
    # print(msg_dict['text'])

    # 过滤邮件
    subject = msg_dict['Subject'].split(' ')
    if subject[0] != 'Ryanair':
        print('# fr filter email: ', msg_dict['Subject'])
        return

    sex = {
        '先生': 'M',
        '女士': 'F',
        '小姐': 'F',
        'Mr': 'M',
        'Mr.': 'M',
        'Mrs': 'F',
        'Mrs.': 'F',
        'Child': 'C',
        'CHD': 'C'
    }
    soup = BeautifulSoup(msg_dict['text'], "lxml")
    ticket_no = soup('table')[11].text.replace('：', ':').split(':')[-1]
    flight_info = soup('table')[21]
    flight_number = flight_info('span')[0].text.replace(' ', '')

    time_str = flight_info('td')[9].text + flight_info('td')[10].strong.text
    if len(time_str) > 15:
        dep_time = time.mktime(
            time.strptime(flight_info('td')[9].text + flight_info('td')[10].strong.text, '%a, %d %b %y%H:%M'))
    else:
        dep_time = time.mktime(
            time.strptime(flight_info('td')[9].text + flight_info('td')[10].strong.text, '%d/%m/%Y%H:%M'))

    name_info = soup('table')[30]('table')[2:]
    name = ''
    gender = ''
    for i in name_info:
        name_list = i('tr')[0].text.replace('\xa0', ' ').split(' ')
        if name == '':
            for i in name_list[1:-1]:
                name = name + i
            name = name_list[-1] + '/' + name
            gender = sex.get(name_list[0])
        else:
            temp_name = ''
            for j in name_list[1:-1]:
                temp_name = temp_name + j
            name = name + ',' + name_list[-1] + '/' + temp_name
            gender = gender + ',' + sex.get(name_list[0])

    flight_type = 1
    ret_time = 0
    if len(soup('table')) > 170:
        ticket_no = soup('table')[11].text.replace('：', ':').split(':')[-1]

        flight_type = 2
        flight_info = soup('table')[29]
        flight_number = flight_number + ',' + flight_info('span')[0].text.replace(' ', '')

        time_str = flight_info('td')[9].text + flight_info('td')[10].strong.text
        if len(time_str) > 15:
            ret_time = time.mktime(
                time.strptime(flight_info('td')[9].text + flight_info('td')[10].strong.text, '%a, %d %b %y%H:%M'))
        else:
            ret_time = time.mktime(
                time.strptime(flight_info('td')[9].text + flight_info('td')[10].strong.text, '%d/%m/%Y%H:%M'))

        name_info = soup('table')[38]('table')[2:]
        name = ''
        for i in name_info:

            name_list = i('tr')[0].text.replace('\xa0', ' ').split(' ')

            if name == '':
                for i in name_list[1:-1]:
                    name = name + i
                name = name_list[-1] + '/' + name
                gender = sex.get(name_list[0])
            else:
                temp_name = ''
                for j in name_list[1:-1]:
                    temp_name = temp_name + j
                name = name + ',' + name_list[-1] + '/' + temp_name
                gender = gender + ',' + sex.get(name_list[0])

    data = {
        "name": name,
        "dep_time": dep_time,
        "ret_time": ret_time,
        "flight_number": flight_number,
        "ticketNo": ticket_no,
        "addtime": time.time(),
        "flight_type": flight_type,
        'gender': gender,
        "email": msg_dict['To'][1:-1]
    }
    # print(data)
    return data
