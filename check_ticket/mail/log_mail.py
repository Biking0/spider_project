# coding: utf-8
import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import parseaddr, formataddr

import settings


def log_mail(log_msg):
    """发送邮件存在出错的情况，两次发送保证稳定"""
    try:
        send_mail(log_msg)
    except:
        send_mail(log_msg)


def send_mail(log_msg):
    """

    :param log_msg: 发送的日志内容
    :return:
    """
    from_addr = settings.LOG_ADDR
    password = settings.LOG_PASSWORD
    to_addr = settings.TO_ADDR
    smtp_server = settings.SMTP_SERVER[0]
    port = settings.SMTP_SERVER[1]
    msg = MIMEText(log_msg, 'plain', 'utf-8')
    # msg['From'] = _format_addr('日志<%s>' % from_addr)
    msg['From'] = formataddr((Header('日志', 'utf-8').encode(), from_addr))
    # msg['To'] = _format_addr('admin<%s>' % 'qiaoliangno1@163.com,qiaoliang@lamudatech.com')
    msg['Subject'] = Header('check ticket error', 'utf-8').encode()

    server = smtplib.SMTP_SSL(smtp_server, port)
    # server.set_debuglevel(1)
    server.login(from_addr, password)
    server.sendmail(from_addr, to_addr, msg.as_string())
    server.quit()


def _format_addr(s):
    # 格式化邮件地址
    name, addr = parseaddr(s)
    print(formataddr((Header(name, 'utf-8').encode(), addr)))
    return formataddr((Header(name, 'utf-8').encode(), addr))


if __name__ == '__main__':
    log_mail('655defgjhsdkjfhbsdhmjf')
