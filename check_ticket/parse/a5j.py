# coding: utf-8
import time
import io
import re
import logging

from pdfminer.pdfparser import PDFParser, PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed


def data_parse(msg_dict):
    logging.propagate = False
    logging.getLogger().setLevel(logging.ERROR)
    data = msg_dict.get('attach').get('Itinerary_PDF.pdf')
    # print(type(data))
    if not data:
        return
    # with open('data/test.pdf', 'wb') as f:
    #     f.write(data)
    # data = open('data/test.pdf', 'rb')
    # 把字节转换成可读取类型
    data = io.BufferedReader(io.BytesIO(data))
    # for i in range(44):
    #     path = 'data/attach/Itinerary_PDF' + str(i) + '.pdf'
    #     data = open(path, 'rb')
    # 用文件对象创建一个文档解析器
    parser = PDFParser(data)
    # 创建一个PDF文档
    doc = PDFDocument()
    # 链接分析器与文档对象
    parser.set_document(doc)
    doc.set_parser(parser)

    # 文档密码，无密码默认空
    doc.initialize()

    # 检查文档是否支持txt转换，不支持略过
    if not doc.is_extractable:
        print('PDF文档无法解析')
        raise PDFTextExtractionNotAllowed
    # 创建一个PDF的资源管理器，来管理共享资源
    rsrcmgr = PDFResourceManager()
    # 创建一个PDF设备对象
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    # 创建一个PDF解释器对象
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    # 循环遍历列表，每次处理一个page内容
    data = ''
    for page in doc.get_pages():
        interpreter.process_page(page)
        # 接受该页面的LTPage对象
        layout = device.get_result()
        # layout是一个LTPage对象，存放page解析出来的LTTextBox，LTFigure，LTimage，LTTextBoxHorizontal等等
        for x in layout:
            if isinstance(x, LTTextBoxHorizontal):
                x = x.get_text()
                data = data + x
    # print(data.encode('utf-8'))
    ticket_no = re.compile('REFERENCE NUMBER:  \n(.*) \nGuest').search(data).group(1)
    # name = re.compile('Guest Details \n(.*\n*.*\n*.*\n*.*\n*.*\n*)\nFlight Details').search(data).group()
    name_str = re.compile('Guest Details \n((.*\n*){1,10})\nFlight Details').search(data).group(1)
    name_list = re.compile('(\d. ((.*)\((.*)\) ){,10})').findall(name_str)
    name = ''
    gender = ''
    for ns in name_list:
        nl = ns[2].strip().split(' ')
        name += nl[-1] + '/' + ''.join(nl[:-1]) + ','
        if ns[3].strip() == 'Adult':
            gender += 'A,'
        elif ns[3].strip() == 'Child':
            gender += 'C,'

    flight_number = re.compile('DG (\n*)\d+|5J (\n*)\d+').search(data).group()
    flight_number = flight_number.replace('\n', '').replace(' ', '')

    dep_time = re.compile('(DG (\n*)\d+|5J (\n*)\d+) \n(.*?\n*.*\(.*\))').search(data).group(4).replace('\n', '')
    dep_time_str = dep_time = re.sub(',(.*?)\(', ',', dep_time)
    dep_time_tup = time.strptime(dep_time_str, '%A %d %B %Y ,%I:%M%p)')
    dep_time = time.mktime(dep_time_tup)
    # dep_time = re.compile('\w+? \d+? \w+? \d+? ,(.*?)\(.*\)').sub('', dep_time)

    data = {
        "name": name.strip(',').replace(' ', '').upper(),
        "dep_time": dep_time,
        "ret_time": '',
        "flight_number": flight_number,
        "ticketNo": ticket_no,
        "addtime": time.time(),
        "flight_type": 1,
        "gender": gender.strip(','),
        "email": msg_dict['To'][1:-1].lower()
    }

    # print(data)

    return data


if __name__ == '__main__':
    data_parse()
# def parse():
#     fp = open('data/attach/Itinerary_PDF.pdf', 'rb') # 以二进制读模式打开
#     # 用文件对象来创建一个pdf文档分析器
#     praser = PDFParser(fp)
#     # 创建一个PDF文档
#     doc = PDFDocument()
#     # 连接分析器 与文档对象
#     praser.set_document(doc)
#     doc.set_parser(praser)
#
#     # 提供初始化密码
#     # 如果没有密码 就创建一个空的字符串
#     doc.initialize()
#
#     # 检测文档是否提供txt转换，不提供就忽略
#     if not doc.is_extractable:
#         raise PDFTextExtractionNotAllowed
#     else:
#         # 创建PDf 资源管理器 来管理共享资源
#         rsrcmgr = PDFResourceManager()
#         # 创建一个PDF设备对象
#         laparams = LAParams()
#         device = PDFPageAggregator(rsrcmgr, laparams=laparams)
#         # 创建一个PDF解释器对象
#         interpreter = PDFPageInterpreter(rsrcmgr, device)
#
#         # 循环遍历列表，每次处理一个page的内容
#         for page in doc.get_pages(): # doc.get_pages() 获取page列表
#             interpreter.process_page(page)
#             # 接受该页面的LTPage对象
#             layout = device.get_result()
#             # 这里layout是一个LTPage对象 里面存放着 这个page解析出的各种对象
#             # 一般包括LTTextBox, LTFigure, LTImage, LTTextBoxHorizontal 等等 想要获取文本就获得对象的text属性，
#             for x in layout:
#                 if (isinstance(x, LTTextBoxHorizontal)):
#                     with open(r'data/attach/1.txt', 'a') as f:
#                         results = x.get_text()
#                         print(results)
#                         f.write(results + '\n')
