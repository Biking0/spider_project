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

from wand.image import Image
from PIL import Image as PI
import pyocr
import pyocr.builders
import io
import sys
import traceback


def data_parse(msg_dict):
    # print('###')
    logging.propagate = False
    logging.getLogger().setLevel(logging.ERROR)
    # print(msg_dict.get('Subject'))
    if not msg_dict.get('Subject')[0] == '您':
        logging.info('# tr filter ')
        return
    # print(type(msg_dict.get('Subject')))
    ticket_no = msg_dict.get('Subject').split(' ')[-1]

    # file_name = 'Itinerary - ' + ticket_no + '.pdf'

    file_name = 'Itinerary – ' + ticket_no + '.pdf'
    # file_name = 'Itinerary - V44DFI.pdf'
    # print(file_name)

    try:

        data = msg_dict.get('attach').get(file_name)

        if not data:
            return
        with open('parse/tr_data/test.pdf', 'wb') as f:
            f.write(data)

        tools = pyocr.get_available_tools()
        if len(tools) == 0:
            print("No OCR tool found")
            sys.exit(1)
        tool = tools[0]
        print("Will use tool '%s'" % (tool.get_name()))

        print(tool.get_available_languages())

        langs = tool.get_available_languages()
        print("Available languages: %s" % ", ".join(langs))
        lang = langs[0]
        print("Will use lang '%s'" % (lang))

        req_image = []
        final_text = []

        image_pdf = Image(filename="parse/tr_data/test.pdf", resolution=400)
        image_jpeg = image_pdf.convert('jpeg')
        image_jpeg.save(filename='parse/tr_data/test.jpeg')

        img_page = Image(image=image_jpeg.sequence[0])
        req_image.append(img_page.make_blob('jpeg'))

        # for img in image_jpeg.sequence:
        #     img_page = Image(image=img)
        #     req_image.append(img_page.make_blob('jpeg'))
        img = req_image[0]
        txt = tool.image_to_string(
            PI.open(io.BytesIO(img)),
            lang=lang,
            builder=pyocr.builders.TextBuilder()
        )

        # 全部数据
        final_text.append(txt)

        # for img in req_image:
        #     txt = tool.image_to_string(
        #         PI.open(io.BytesIO(img)),
        #         lang=lang,
        #         builder=pyocr.builders.TextBuilder()
        #     )
        #     final_text.append(txt)
        # print(final_text)
        a = 0
        for text in final_text[0].replace('  ', '').replace('   ', '').split(' '):
            # print('#' * 66, a)
            # print(text)
            a = a + 1

        print('long: ', len(final_text))
        print('# 107', final_text)

        flight_number_list = re.findall(r'\((.*?)\)', final_text[0])
        flight_number = ''
        for i in flight_number_list:
            if i[0:2] == 'TR':
                if flight_number == '':
                    flight_number = i
                else:
                    flight_number = flight_number + ',' + i

        print('flight_number: ', flight_number)

        gender_dict = {
            '先生': 'M',
            '女士': 'F',
            '夫人': 'F',
        }

        name_str_list = final_text[0].split('Umber')
        gender = ''
        name_list = []
        p = 0
        name_str = ''

        # 处理乘客姓名
        for i in name_str_list[1:]:
            # print('# i: ', i, p)
            # p = p + 1

            # 列表，全部名字
            name_str = i.replace('\n', ' ').replace('  ', '').replace('   ', '').replace('-', '').replace('“',
                                                                                                          ' ').strip().split(
                ' ')
            # name_str = i.replace('  ', '').replace('   ', '').replace('-', '').strip().split(' ')
            print('# 121 namestr: ', name_str)

            count = 0

            # 单人
            for j in range(len(name_str)):

                # print('### 131: ', name_str[j], len(name_str[j]))
                if len(name_str[j]) > 8:
                    # print(name_str[j])
                    if name_str[j][:-2] == 'KrisFlyer':
                        # print('###################### KrisFlyer')
                        count = j
                        break

                if name_str[j] == '' or name_str[j] == '-' or name_str[j][-2:] == 'kg' or name_str[j][
                                                                                          :-2] == 'KrisFlyer' or \
                        name_str[j] == ' ' or name_str[j] == '-' or len(name_str[j]) == 0:
                    name_str.remove(name_str[j])
                if len(name_str[j]) > 20:
                    count = j
                    break

            # ['女士', 'THANYALAK', '-', 'SRIJUMPA', '先生', 'YONG', 'JIN', 'CRUZ']
            name_str = name_str[:count]
            # print('### 139: ', name_str, len(name_str))

            # # 多人
            # for j in range(len(name_str)):
            #     if name_str[j] == '' or name_str[j] == '-' or len(name_str[j]) == 0:
            #         name_str.remove(name_str[j])
            #     if len(name_str[j]) > 20:
            #         count = j
            #         break

            name_str = name_str[:count]
            print('### 148: ', name_str, len(name_str))

            # 不统计返程
            break

        # 去空
        for i in name_str:
            if len(i) == 0:
                name_str.remove(i)

        temp_name_list = []
        temp_a = []
        temp_b = []
        # 获取乘客姓名
        for i in range(len(name_str)):

            # _temp
            if i != 0 and name_str[i] in gender_dict:
                for j in name_str[i:]:
                    temp_b.append(j)
                break
            temp_a.append(name_str[i])

        temp_name_list.append(temp_a)
        if len(temp_b) != 0:
            temp_name_list.append(temp_b)

        print('# 179', temp_name_list)

        name = ''
        for i in temp_name_list:
            if name == '':
                for j in i[1:-1]:
                    name = name + j
                name = i[-1] + '/' + name
                gender = gender_dict.get(i[0])
            else:
                temp_name = ''
                for j in i[1:-1]:
                    temp_name = temp_name + j
                name = name + ',' + i[-1] + '/' + temp_name
                gender = gender + ',' + gender_dict.get(i[0])

        print('# name', name, gender)

        # 出发时间
        name_str_list = name_str_list[0].replace('\n', ' ').replace('  ', '').replace('   ', '').replace('-',
                                                                                                         '').replace(
            '“', ' ').strip().split(' ')

        print('# 221 deptime ', name_str_list)

        dep_time = ''
        dep_date = ''
        ret_time = 0
        ret_date = ''
        for i in range(len(name_str_list)):
            if name_str_list[i] == '值机时间':

                if dep_time != '':
                    ret_time = name_str_list[i - 1].split(')')[1]
                    # break
                if dep_time == '':
                    dep_time = name_str_list[i - 1].split(')')[1]

            if name_str_list[i] == 'Fare':

                # if dep_date == '':
                #     dep_date = name_str_list[i - 1].replace('年', '-').replace('月', '-').replace('日', '')
                # ret_date = name_str_list[i - 1].replace('年', '-').replace('月', '-').replace('日', '')

                # print('# 226 ',name_str_list[i-1])
                if dep_date != '':
                    ret_date = name_str_list[i - 1].replace('年', '-').replace('月', '-').replace('日', '')
                    break
                dep_date = name_str_list[i - 1].replace('年', '-').replace('月', '-').replace('日', '')

        # print('# deptime: ', dep_date, dep_time, ret_date, ret_time)
        dep_time = time.mktime(time.strptime(dep_date + dep_time, '%Y-%m-%d%H:%M'))

        flight_type = 1
        if ret_date != '' and ret_time != '':
            ret_time = time.mktime(time.strptime(ret_date + ret_time, '%Y-%m-%d%H:%M'))
            flight_type = 2

        # ticket_no = 123

        data = {
            "name": name.strip(',').replace(' ', '').upper(),
            "dep_time": dep_time,
            "ret_time": ret_time,
            "flight_number": flight_number,
            "ticketNo": ticket_no,
            "addtime": time.time(),
            "flight_type": flight_type,
            "gender": gender.strip(','),
            "email": msg_dict['To'][1:-1].lower()
            # "email": 123
        }

    except:
        print(traceback.print_exc())
        return

    print('# data: ', data)

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
