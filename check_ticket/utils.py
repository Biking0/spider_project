# coding: utf-8
import json
import time
import traceback

import requests
from datetime import datetime

from mail.log_mail import log_mail
import settings


def push_data(data_list):
    # print(data_list)
    dict_date = {data_list[x].get('received_time'): data_list[x] for x in range(len(data_list))}
    # print(dict_date)
    list_date = [x for x in dict_date.keys()]
    # print(list_date)
    list_date.sort()
    # print(list_date)
    data_list = [dict_date.get(x) for x in list_date]
    step = 10
    data_sort = [data_list[i: i + step] for i in range(0, len(data_list), step)]
    for data_s in data_sort:
        num = len(data_s)
        data = json.dumps({'data': data_s})
        # 测试库
        # url = settings.PUSH_TEST_URL
        # 正式库
        url = settings.PUSH_URL
        for i in range(5):
            error_data = None
            try:
                res = requests.post(url, data, timeout=settings.PUSH_TIMEOUT)
                if json.loads(res.text).get('status') != 0:
                    error_data = 'return status error:%s' % res.text
                    print(error_data)
                else:
                    if json.loads(res.text).get('err_num') > 0:
                        error_msg = "Upload data error\t\n error_msg: \n%s\t\n error_data: \n%s" % (res.text, data)
                        log_mail(error_msg)
                        print('Send an email with an error message')
                    else:
                        # print(data)
                        print("pushData: %s" % num)
                    time.sleep(1)
                    break
            except Exception:
                # traceback.print_exc()
                error_data = traceback.format_exc()
                print('push data error')
            finally:
                if i == 4:
                    error_msg = "Retry 5 upload errors\t\n error_msg: \n%s\t\n error_data: \n%s" % (error_data, data)
                    log_mail(error_msg)
                    print('Too many failures, give up uploading, send error mail')
            time.sleep(5)


def write_json(num_qq=0, num_163=0):
    data = json.dumps({'num_qq': num_qq, 'num_163': num_163})
    with open('data/mail_num.json', 'wb') as f:
        f.write(str.encode(data))
    return 'Write Mail Num OK!'


def read_json():
    with open('data/mail_num.json', 'rb') as f:
        data = json.loads(f.read().decode('utf-8'))
        num_qq = data.get('num_qq')
        num_163 = data.get('num_163')
    return num_163, num_qq


def u2_year(dep_time):
    if dep_time[1] < datetime.now().month:
        return str(datetime.now().year + 1)
    else:
        return str(datetime.now().year)


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value


def to_bytes(bytes_or_str):
    if isinstance(bytes_or_str, str):
        value = bytes_or_str.encode('utf-8')
    else:
        value = bytes_or_str
    return value


