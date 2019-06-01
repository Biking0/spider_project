# encoding=utf-8
import mitmproxy.http
from mitmproxy import ctx, http
import re, struct
import io, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


class Joker:
    def request(self, flow: mitmproxy.http.HTTPFlow):
        pass
        # # print('joker: ', '6' * 66)
        # if flow.request.host != "www.baidu.com" or not flow.request.path.startswith("/s"):
        #     return
        #
        # if "wd" not in flow.request.query.keys():
        #     ctx.log.warn("can not get search word from %s" % flow.request.pretty_url)
        #     return
        #
        # ctx.log.info("catch search word: %s" % flow.request.query.get("wd"))
        # flow.request.query.set_all("wd", ["360搜索"])

    def response(self, flow: mitmproxy.http.HTTPFlow):

        response = flow.response

        info = ctx.log.info

        # info(str(response.status_code))
        #
        # info(str(response.headers))
        #
        # info(str(response.cookies))

        info(str(response.text))

        a = []

        for line in open("./mitmproxy_js/js_key.txt"):
            line_str = line.replace('\\\\', '\\').replace(' ', '').replace('\n', '')
            a.append(line_str)
        # print (a[352], a[588], a[80])
        selenium = a[80]
        driver = a[352]
        webdriver = a[588]
        # print ('##########################', webdriver)
        chrome = a[668]
        msvisibilitychange = a[57]
        visibilitychange = a[144]
        webkitvisibilitychange = a[278]
        hidden = a[438]
        mozvisibilitychange = a[506]
        location = a[519]
        onblur = a[633]
        onfocus = a[425]
        navigator = a[632]

        if '_bm/cbd-1-35' in flow.request.url:
            print('cd########################')
            flow.response.text = flow.response.text.replace(webdriver, driver)
            flow.response.text = flow.response.text.replace(msvisibilitychange, driver)
            flow.response.text = flow.response.text.replace(visibilitychange, driver)
            flow.response.text = flow.response.text.replace(hidden, driver)
            flow.response.text = flow.response.text.replace(mozvisibilitychange, driver)
            flow.response.text = flow.response.text.replace(onblur, onfocus)

            # fw = open('cd.txt', 'w')
            # fw.write(flow.response.text)
            # fw.close()
            # print(flow.response.text)
            return

        if 'akam/10' in flow.request.url:
            print('ak########################')
            flow.response.text = flow.response.text.replace(webdriver, driver)
            flow.response.text = flow.response.text.replace(msvisibilitychange, driver)
            flow.response.text = flow.response.text.replace(visibilitychange, driver)
            flow.response.text = flow.response.text.replace(webkitvisibilitychange, driver)
            flow.response.text = flow.response.text.replace(hidden, driver)
            flow.response.text = flow.response.text.replace(mozvisibilitychange, driver)
            flow.response.text = flow.response.text.replace(onblur, onfocus)

            # fw = open('ak.txt', 'w')
            # fw.write(flow.response.text)
            # fw.close()
            # print(flow.response.text)
            return

        # BR
        if 'book.evaair.com/br' in flow.request.url:
            ctx.log.info('br-js  ########################')
            flow.response.text = flow.response.text.replace('webdriver', 'we1bdri1ver')

            # fw = open('ak.txt', 'w')
            # fw.write(flow.response.text)
            # fw.close()
            # print(flow.response.text)
            return

        # booking.volotea.com
        if 'booking.volotea.com/_Incapsula' in flow.request.url:
            ctx.log.info('booking.volotea  ########################')
            flow.response.text = flow.response.text.replace('webdriver', 'webdri1ver')

        if flow.request.host != "www.so.com":
            return

        text = flow.response.get_text()
        text = text.replace("搜索", "请使用谷歌")
        flow.response.set_text(text)

    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.host == "www.google.com":
            flow.response = http.HTTPResponse.make(404)
