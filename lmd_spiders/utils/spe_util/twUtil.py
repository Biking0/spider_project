from datetime import datetime
import time

def format_duration(time_str):

    li_time = time_str.split(' ')
    return '%s:%s' % (li_time[0][:-1], li_time[1][:-1])

def format_time(time_str):
    ti_time = time.strptime(time_str, '%Y%m%d%H%M%S')
    return time.mktime(ti_time)



if __name__ == '__main__':
    # print(format_duration('01h 10m'))
    print(format_time('20180429081500'))