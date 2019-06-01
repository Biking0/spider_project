# encoding=utf-8
import mitmproxy.http
from mitmproxy import ctx, http
import re, struct, typing, time
# from utils import pubUtil
import io, sys, requests, random, logging, json, traceback

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


class Joker:

    def __init__(self):
        self.proxy_flag = True
        self.ip = ''

    # 从小池子中获取IP
    def jq_get_proxy(self):
        # num = spider.custom_settings.get('PROXY_TRY_NUM', 10)
        # if spider.isOK:
        #     return self.proxy
        # if self.proxy_count < num and self.proxy != '':
        #     self.proxy_count = self.proxy_count + 1
        #     logging.info('using old proxy:' + self.proxy)
        #     return self.proxy
        #
        # self.proxy_count = 0
        # if self.token_count >= 5:

        #     logging.info('# update token')
        #     self.token_count = 0
        #     self.get_token(spider)
        #     return
        proxy = ''
        GET_PROXY_URL = 'http://dx.proxy.jiaoan100.com/proxy/getproxy?'
        try:
            params = {'carrier': 'jq'}
            li = json.loads(requests.get(GET_PROXY_URL, params=params, timeout=60,
                                         verify=False).text)
            logging.info('Proxy Num: ' + str(len(li)))
            logging.info(str(li))
            # proxy = random.choice(li).decode('ascii') or ''
            proxy = random.choice(li)
            # self.token_count = self.token_count + 1
        except:
            traceback.print_exc()
            logging.info('get proxy error....')
            return
        finally:
            # spider.proxy_flag = False
            return proxy

    def proxy_address(self, flow: http.HTTPFlow) -> typing.Tuple[str, int]:
        # Poor man's loadbalancing: route every second domain through the alternative proxy.
        ctx.log.info("#################### test_joker")
        # print('####################', flow.request.host)

        # return ("localhost", 1080)
        # return ("59.125.31.116", 45965)
        # if self.proxy_flag:
        #     while True:
        #
        #         self.ip = self.jq_get_proxy().split(':')
        #         if len(self.ip) > 0 and len(self.ip[0]) > 0:
        #             break
        #         time.sleep(2)
        # self.proxy_flag = False
        #
        # ctx.log.info('####### ip: ' + str(self.ip))
        # return (self.ip[0], int(self.ip[1]))
        return ("45.70.107.56", 8080)
        # return ("110.74.221.230", 52072)
        # return ("201.90.36.194", 3128)
        # return ("61.9.82.34", 53534)
        # return ("89.176.251.2", 55102)
        # return ("81.17.131.59", 8080)

        # if hash(flow.request.host) % 2 == 1:
        #     # return ("localhost", 1080)
        #     # return ("59.125.31.116", 45965)
        #     return ("110.74.221.230", 52072)
        #     # return ("201.90.36.194", 3128)
        #     # return ("61.9.82.34", 53534)
        # else:
        #     # return ("localhost", 1080)
        #     # return ("59.125.31.116", 45965)
        #     return ("110.74.221.230", 52072)
        #     # return ("201.90.36.194", 3128)
        #     # return ("61.9.82.34", 53534)
        #     return ("89.176.251.2", 55102)

    def request(self, flow: mitmproxy.http.HTTPFlow):




        # print('32'*66)
        address = self.proxy_address(flow)
        if flow.live:
            # print('' * 66)
            flow.live.change_upstream_proxy_server(address)
        # self.proxy_flag = True

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
        info(str(response.text))

        status_code = flow.get_state().get('status_code')
        if not status_code or status_code != 200 or status_code != '200':
            ctx.log.info("##################### " + str(flow.get_state().get('status_code')))
            # print('######################################################', flow.get_state().get('status_code'))
            self.proxy_flag = True
            return

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
        if flow.request.host != "www.so.com":
            return

        text = flow.response.get_text()
        text = text.replace("搜索", "请使用谷歌")
        flow.response.set_text(text)

    def http_connect(self, flow: mitmproxy.http.HTTPFlow):
        if flow.request.host == "www.google.com":
            flow.response = http.HTTPResponse.make(404)
