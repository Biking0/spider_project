# coding: utf-8
import traceback
import time

from main.main import main
from mail.log_mail import log_mail

if __name__ == '__main__':
    while True:
        try:
            main()
        except:
            traceback.print_exc()
            error_msg = "run error\t\n error_msg: \n%s" % traceback.format_exc()
            log_mail(error_msg)
            print('Send an email with an error message')

        time.sleep(20 * 60)
