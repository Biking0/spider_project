# coding: utf-8
import poplib

import settings

from func_timeout import func_set_timeout

# 因为存在垃圾大邮件的问题，python默认限制了行的大小，在这里增大10倍
poplib._MAXLINE=settings.MAXLINE


@func_set_timeout(100)
def login_mail(email, password, pop3_server, transport_protocols='plaintext'):
    # 链接服务器，判断协议
    # if transport_protocols == 'plaintext':
    #     server = poplib.POP3(pop3_server)
    try:
        if transport_protocols == 'ssl':
            server = poplib.POP3_SSL(pop3_server)
        else:
            server = poplib.POP3(pop3_server)
    except :
        server = poplib.POP3(pop3_server)
    # 打开调试信息
    server.set_debuglevel(1)

    # 打印pop3服务器欢迎文字
    # print(server.getwelcome())

    # 身份认证
    server.user(email)
    server.pass_(password)

    return server
