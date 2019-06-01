# encoding:utf-8

import sys, os, time
from utils.pubUtil import timezone_is_cst

timezone_is_cst() # 判断本地时区
    
argv = sys.argv
host_name = argv[1]
num = argv[2] if len(argv)>2 else 1
proxy = argv[3] if len(argv)>3 else ''
while True:
    os.system('scrapy crawl w6 -a host_name=%s -a num=%s -a proxy=%s' % (host_name, num, proxy))
    time.sleep(8)
