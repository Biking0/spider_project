# encoding:utf-8
import os
import csv
import sys
import random
from datetime import datetime, timedelta

from dateutil.tz import tzlocal


def gen_cmd(carrier, argv):
    if len(argv) < 2:
        print('pls input like this:')
        print('python be_spider.py lin 1 ')
        sys.exit()

    num = 1 if len(argv) < 3 else argv[2]  # 爬虫序号

    arg_set = set()  # 生成后面的参数
    arg_big = set()
    if len(argv) > 3:
        for arg in argv[3:]:
            if arg == '1':  # 兼容以前的proxy版本的
                arg_set.add('proxy=1')
            else:
                k, v = arg.split('=')
                if k == 'local':
                    arg_big.add('CLOSESPIDER_TIMEOUT=0')

                if k.isupper():
                    arg_big.add(arg.replace(' ', ''))
                else:
                    arg_set.add(arg.replace(' ', ''))
    arg_str = ''
    if len(arg_set):
        arg_str = ' -a ' + ' -a '.join(arg_set)
    if len(arg_big):
        arg_str += ' -s ' + ' -s '.join(arg_big)

    cmd = 'scrapy crawl %s -a host_name=%s -a num=%s' % (carrier, argv[1], num) + arg_str
    return cmd


def timezone_is_cst():
    if datetime.now(tzlocal()).tzname() != 'CST':
        print('the timezone is not cst. please config it by this command:')
        print('1. sudo tzselect # Asia -> China -> yes')
        print('2. sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
        print('3. date # check it again !')
        sys.exit()


def get_task(carrier, step=1, days=7, st=1):
    input_file = open(os.path.join(r'utils/src', '%s.csv' % carrier.upper()))
    reader = csv.reader(input_file)
    datas = list(reader)
    input_file.close()
    thisday = datetime.now() + timedelta(days=st)
    random.shuffle(datas)
    for i in range(0, days, step):
        _date = thisday + timedelta(days=i)
        _dt = _date.strftime('%Y%m%d')
        for data in datas:
            if not data or not len(data):
                continue
            print(['%s-%s:%s:%s' % (data[0], data[1], _dt, step)])
            yield ['%s-%s:%s:%s' % (data[0], data[1], _dt, step)]
