# encoding=utf-8
import mitmproxy.http
from mitmproxy import ctx
import io, sys, requests, random, logging, json, traceback
from utils import dataUtil

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf8')


class JqDispath:

    def __init__(self):
        self.proxy_flag = True
        self.ip = ''
        # 通过机场获取城市
        self.portCitys = dataUtil.get_port_city()
        self.task = []
        self.buffer = []
        # 处理js过滤关键字
        self.js_list = []
        for line in open("src/js_key.txt"):
            line_str = line.replace('\\\\', '\\').replace(' ', '').replace('\n', '')
            self.js_list.append(line_str)

    def request(self, flow: mitmproxy.http.HTTPFlow):

        pass
        # # 切换代理
        # address = self.proxy_address()
        # if flow.live:
        #     flow.live.change_upstream_proxy_server(address)
        # self.proxy_flag = True

    def response(self, flow: mitmproxy.http.HTTPFlow):

        # 测试中，动态切换代理
        # status_code = flow.get_state().get('status_code')
        # if not status_code or status_code != 200 or status_code != '200':
        #     ctx.log.info("#" + str(flow.get_state().get('status_code')))
        #     self.proxy_flag = True
        #     return

        # JQ过滤
        if '_bm/cbd-1-35' in flow.request.url:
            self.jq_progress_cd(flow)

        # JQ过滤
        if 'akam/10' in flow.request.url:
            self.jq_progress_ak(flow)

    def jq_progress_cd(self, flow):
        ctx.log.info('# cd')
        self.jq_repalce(flow)

    def jq_progress_ak(self, flow):
        ctx.log.info('# ak')
        self.jq_repalce(flow)

    # JQ替换关键字
    def jq_repalce(self, flow):
        flow.response.text = flow.response.text.replace(self.js_list[588], self.js_list[352])
        flow.response.text = flow.response.text.replace(self.js_list[57], self.js_list[352])
        flow.response.text = flow.response.text.replace(self.js_list[144], self.js_list[352])
        flow.response.text = flow.response.text.replace(self.js_list[438], self.js_list[352])
        flow.response.text = flow.response.text.replace(self.js_list[506], self.js_list[352])
        flow.response.text = flow.response.text.replace(self.js_list[633], self.js_list[425])
        return
