# coding: utf-8
import traceback
import time

import poplib
from mail.login_mail import login_mail
from mail.manage_mail import print_info
from mail.log_mail import log_mail
from mail.get_msg import get_msg

import utils
import settings

mail_config = settings.MAIL_CONFIG
carrier_parse = settings.PARSE_CARRIER
# 存储邮件数量
data_list = []
# 获取上次跑过的邮件id
num_163, num_qq = utils.read_json()
print('上次运行到：\r\n\t163：%s\r\n\tqq：%s' % (num_163, num_qq))


def mail_handle():
    global num_163, num_qq
    # 遍历邮箱服务商
    for mailbox_server in mail_config:
        print('crawling %s mailbox' % mailbox_server)
        # 获取账号，密码，端口, 网络连接类型
        email, password, pop3_server, transport_protocols = (x for x in mail_config.get(mailbox_server))
        # 登录邮件服务器,防止出错，再次请求
        server = None
        for num_error in range(10):
            try:
                server = login_mail(email, password, pop3_server, transport_protocols)
                break
            except Exception as e:
                # if num_error == 9:
                #     raise e
                pass
        # 显示邮件数量和占用空间
        print('Messages:%s.\nSize:%s' % server.stat())

        # # 显示邮件编号
        # resp, mails, octets = server.list()

        # 获取最新的邮件，索引是从最早的邮件开始
        max_num = server.stat()[0]
        # 获取任务数量，同时替换最大任务数据
        if mailbox_server == '163':
            task_num = max_num - num_163 + 50
            num_163 = max_num
        else:
            task_num = max_num - num_qq + 50
            num_qq = max_num
        # max_num = 59319
        # task_num = 1000
        for i in range(task_num):
            index = max_num - i
            # index=60458
            msg, error_data = None, ''
            for x in range(5):  # 为防止程序卡死，最多可重试5次
                try:
                    msg = get_msg(server, index)
                    break
                except:
                    print('获取邮件出错，等待1秒重新请求。')
                    error_data = traceback.format_exc()
                    server = login_mail(email, password, pop3_server, transport_protocols)
                if x == 4:
                    error_msg = "邮箱：%s\t\n\r出错邮件：%s\t\n\r错误信息：%s" % (email, index, error_data)
                    log_mail(error_msg)
                    print('get mail error,send error msg')
                time.sleep(1)
            if not msg:
                # 发现QQ邮箱的退信会出现这种问题
                print("邮件内容出错，邮件编号：%s" % index)
                continue

            # 展示邮件信息
            msg_dict = print_info(msg)
            yield msg_dict
        server.quit()


def forward_parse(msg_dict):
    # print(msg_dict.get('From'))
    """

    :param msg_dict: 传入分析的数据字典
    """
    for key in carrier_parse:
        if msg_dict.get('From').find(key) < 0:
            continue
        try:
            # print(key)
            data = carrier_parse.get(key).data_parse(msg_dict)
        except Exception:
            # 出现异常，保存异常信息并发送邮件
            msg_dict.pop('text')
            error_msg = "carrier: \n%s\t\n\n" \
                        "error_msg: \n%s\t\n\n" \
                        "error_data: \n%s" % (key, traceback.format_exc(), msg_dict)
            log_mail(error_msg)
            print('Send an email with an error message')

            return

        if data:
            # 数据出现错误时发送日志邮件
            if data.get('error_data'):
                msg_dict.pop('text')
                error_msg = "carrier: \n%s\t\n\n" \
                            "error_msg: \n%s\t\n\n" \
                            "error_data: \n%s" % (key, data.get('error_data'), msg_dict)
                log_mail(error_msg)
                print('Send an email with an error message')
                return

            # 增加邮件时间
            data['received_time'] = msg_dict.get('Received')
            data_list.append(data)
            # print(data)


def main():
    for msg_dict in mail_handle():
        forward_parse(msg_dict)
        # msg_dict['text'] = msg_dict.get('text')[:200]
        # print(msg_dict)
    # 把数据进行统一上传
    utils.push_data(data_list)
    # 跑取的邮件数量进行存储
    r_or_w = utils.write_json(num_qq=num_qq, num_163=num_163)
    print(r_or_w)
