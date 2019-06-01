import time

def change_to_int(hms):
    h, m, s = hms.split(':')
    return int(h) * 3600 + int(m) * 60 + int(s)

def time_is_valid(st_time, en_time):
    current_str = time.strftime('%H:%M:%S', time.localtime(time.time()))
    current_int = change_to_int(current_str)
    if current_int >= st_time and current_int <= en_time:
        return True
    return False

def get_sleep_time(st_time):
    current_str = time.strftime('%H:%M:%S', time.localtime(time.time()))
    current_int = change_to_int(current_str)
    return change_to_int('24:00:00') - current_int + st_time