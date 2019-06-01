# coding: utf-8
import time
import traceback
from email.header import decode_header
from email.utils import parseaddr

from mail.log_mail import log_mail

a = 0


def print_info(msg, indent=0, data=dict()):
    """
    这个函数使用了递归，因存在多种的邮件格式，和一个邮件存在不同的内容，用作存储之用
    :param msg: 传递过来邮件的全部信息
    :param indent: 用作提取收发件人使用，只调用一次
    :param data: 获取的数据存储在这里面
    :return:返回数据
    """
    # 获取收发件人和标题
    if indent == 0:
        data = get_header(msg, data)
        data['attach'] = get_attach(msg)

    # 当存在多个内容时遍历出来
    if msg.is_multipart():
        parts = msg.get_payload()
        for n, part in enumerate(parts):
            # print('%spart %s' % (' ' * indent, n))
            data['part%s' % n] = n
            # print('%s-------------------' % (' ' * indent))
            data = print_info(part, indent + 1, data=data)
    else:
        content_type = msg.get_content_type()
        if content_type == 'text/plain' or content_type == 'text/html':
            content = msg.get_payload(decode=True)
            charset = guess_charset(msg)
            if charset:
                # 会发生解析错误的现象
                # 默认Unicode编码可以解决
                # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xf3 in position 430: invalid continuation byte
                try:
                    content = content.decode(charset)
                except UnicodeDecodeError:
                    content = str(content)
            # print('%sText: %s' % (' ' * indent, content))
            data['text'] = content
        else:
            # print('%sAttachmen: %s' % (' ' * indent, content_type))
            data['attachmen'] = content_type
    return data


# 用作解析代码
def decode_str(s):
    value, charset = decode_header(s)[0]
    if charset:
        if charset == 'gb2312':
            charset = 'gbk'
        value = value.decode(charset)
    return value


# 用作解析代码
def guess_charset(msg):
    charset = msg.get_charset()
    if charset is None:
        content_type = msg.get('Content-Type', '').lower()
        pos = content_type.find('charset=')
        if pos >= 0:
            charset = content_type[pos + 8:].split(';')[0].strip()
    return charset


# 获取收发件人，标题
def get_header(msg, data):
    # 把发件人，收件人，标题导出来
    for header in ['From', 'To', 'Subject', 'Received']:
        value = msg.get(header, '')
        if value:
            if header in ['Subject', 'Received']:
                value = decode_str(value)
                if header == 'Received':
                    value = get_date(value)
            else:
                hdr, addr = parseaddr(value)
                name = decode_str(hdr)
                value = u'%s<%s>' % (name, addr)
        # print('%s%s: %s' % (' ' * indent, header, value))
        data[header] = value
    return data


# 保存邮件附件
def get_attach(msg):
    attach_name = {}
    for part in msg.walk():
        filename = part.get_filename()
        if filename:
            filename = decode_str(filename).replace("\r", '').replace("\n", '')
            # if filename == 'Itinerary_PDF.pdf':
            #     global a
            #     filename = 'Itinerary_PDF' + str(a) + '.pdf'
            #     a += 1
            #
            # print(filename)
            data = part.get_payload(decode=True)
            attach_name[filename] = data
            # with open('data/attach/%s' % filename, 'wb') as f:
            #     f.write(data)
            #     attach_name.append(filename)
    return attach_name

def get_date(value):
    try:
        date = value.split(';')[-1].strip().split(' +0800')[0]
        tuple_time = time.strptime(date, '%a, %d %b %Y %H:%M:%S')
        value = time.mktime(tuple_time)
    except Exception:
        traceback.print_exc()
        error_msg = "run error\t\n error_msg: \n%s" % traceback.format_exc()
        log_mail(error_msg)
        print('Send an email with an error message')

    return value


if __name__ == '__main__':
    a = None
    print(type(a))
    if a:
        print(1)
    else:
        print(2)