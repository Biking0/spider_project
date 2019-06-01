# coding: utf-8
from email.parser import Parser

from func_timeout import func_set_timeout


@func_set_timeout(100)
def get_msg(server, index):
    resp, lines, octets = server.retr(index)

    # lines存储了邮件的原始文本的每一行
    try:
        msg_content = b'\r\n'.join(lines).decode('utf-8')
    except UnicodeDecodeError:
        # 目前发现QQ的邮箱退信出现这种问题，页面无法解析，暂时先忽略掉
        return None
    # 解析邮件
    msg = Parser().parsestr(msg_content)
    return msg
