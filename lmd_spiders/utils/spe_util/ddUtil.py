from datetime import datetime, timedelta
import time

def analysisData(data):
    p = data.split(':')
    fromTo = p[0].split('-')
    dep = fromTo[0]
    to = fromTo[1]
    dt = p[1]
    days = p[2]
    dt_datetime = datetime.strptime(dt, '%Y%m%d')
    dt_str = dt_datetime.strftime('%Y/%m/%d')
    return (dt_str, dep, to, days)

def get_real_date(date_str, diff_days):
    date_datetime = datetime.strptime(date_str, '%Y%m%d')
    days = timedelta(days=diff_days)
    date_datetime += days
    return date_datetime.strftime('%Y/%m/%d')

def str_to_stamp(time_str):
    ti_time = time.strptime(time_str, '%m/%d/%Y %H:%M')
    return time.mktime(ti_time)

def format_duration(d_dict):
    h = d_dict.get('Hour')
    m = d_dict.get('Minute')
    return '%s:%s' % (str(h).rjust(2, '0'), str(m).rjust(2, '0'))


if __name__ == '__main__':
    # print(str_to_stamp('05/05/2018 06:00'))
    print(format_duration({
                        "Hour": 1,
                        "Minute": 10
                    }))