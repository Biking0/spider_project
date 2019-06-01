# encoding:utf-8

from dateutil.tz import tzlocal
from datetime import datetime
import sys


def timezone_is_cst():
    '''
    判断时区是否是中国上海
    '''
    try:
        if datetime.now(tzlocal()).tzname() != 'CST':
            print('the timezone is not cst. please config it by this command:')
            print('1. sudo tzselect # Asia -> China -> yes')
            print('2. sudo cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime')
            print('3. date # check it again !')
            sys.exit()
    except:
        print('Use Windows will report error, do not close temporarily!!!')


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
