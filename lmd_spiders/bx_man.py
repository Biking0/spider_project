# encoding:utf-8
import os
import sys
import time
from utils import pubUtil

pubUtil.timezone_is_cst()  # 判断时区

CARRIER = 'bx'
argv = sys.argv

cmd = pubUtil.gen_cmd(CARRIER, argv)

while True:
    os.system(cmd)
    time.sleep(8)
