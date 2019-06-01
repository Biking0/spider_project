# encoding=utf-8

import mitmproxy.http
from mitmproxy import ctx
import typing
from parse.wn import WnParser
import time
from utils import pubUtil


class WnDispath:

    def __init__(self):
        self.proxy_flag = True
        self.ip = ''
        self.wn = WnParser(None, '1')
        self.ip_use_time = 0

    def request(self, flow: mitmproxy.http.HTTPFlow):
        print('1' * 66)
        # pass
        # 切换代理
        address = self.proxy_address()
        if flow.live:
            self.ip_use_time = time.time()
            flow.live.change_upstream_proxy_server(address)
        self.proxy_flag = True

    def response(self, flow: mitmproxy.http.HTTPFlow):
        print('#' * 66)
        ctx.log.info('# match wn data')
        print(flow.request.headers)

        # 测试中，动态切换代理
        # status_code = flow.get_state().get('status_code')
        # if not status_code or status_code != 200 or status_code != '200':
        #     ctx.log.info("#" + str(flow.get_state().get('status_code')))
        #     self.proxy_flag = True
        #     return

        # # WN过滤，手机端
        # if '/mobile-air-booking/page/flights/products' in flow.request.url:
        #     ctx.log.info('# match wn data')
        #     self.wn_progress_parse(flow.response)

        # WN添加js
        if '/air/booking/select.html?' in flow.request.url:
            ctx.log.info('# match wn search')
            self.wn_progress_addjs(flow)

        # WN PC web端目标数据过滤
        if '/air-booking/page/air/booking/shopping' in flow.request.url:
            ctx.log.info('# match wn data')
            self.wn.parse(flow)

        # WN 航线不存在
        if '/air/booking/index.html' in flow.request.url:
            ctx.log.info('# match wn data')
            self.wn_progress_addjs(flow)

        # WN selenium特征过滤
        if '/en_US/fbevents.js' in flow.request.url:
            ctx.log.info('# ##############################################################################')
            # ctx.log.info('# match wn data')
            # self.wn_progress_addjs(flow)

        print(flow.request.headers)

    # WN添加js
    def wn_progress_addjs(self, flow):
        ctx.log.info('# wn js')

        js_one_way = '''<script src="https://cdn.staticfile.org/jquery/1.10.2/jquery.min.js"></script>
        <script>
    $(function () {
        var start;
        var end;
        var search = 0;
        var n = 4000;
        var m = 7000;
        var c = m-n+1;
        var addbody = function () {
            var element = document.createElement('div');
            element.id = 'lamuda';
            document.body.appendChild(element);
        };
        var handle = setInterval(function () {
            console.log('search'+search)
            var es = document.getElementsByClassName("calendar-strip--item");
            if (es && es.length > 3) {
                !start && (start = new Date("2019 " + es[2].getElementsByClassName('calendar-strip--date')[0].innerText));
                start && (end = new Date("2019 " + es[2].getElementsByClassName('calendar-strip--date')[0].innerText));
                if (start && end) {
                    var diff = end - start;
                    if (diff > (24 * 60 * 60 * 30 * 1000)) {
                        console.log('close window')
                        addbody();
                        //clearInterval(handle);
                        //return;
                    }
                }
                es[3].getElementsByTagName('a')[0].click();
                search = 0;
            } else {
                search = search + 1;
                var errs = document.getElementsByClassName("form-control--error swa-g-error")
				if(search > 10000 || (errs && errs.length > 0)){
				   console.log('no airline')
				   addbody();
				   clearInterval(handle);
				   return;
				}
                var se = document.getElementById('form-mixin--submit-button');
                se && se.click();
            }
        }, Math.floor(Math.random() * c + n));


    setInterval(function(){
	   function getRandomInt(max) {
	      return Math.floor(Math.random() * Math.floor(max));
	    }

	    var screenX = window.screenX;
	    var screenY = window.screenY;
	    var height = window.innerHeight;
	    var width  = window.innerWidth;
	    var random = getRandomInt(100);
	    var event = new MouseEvent('mousemove', {
		   view: window,
		   bubbles: true,
		   screenX: screenX + width / 2 + random,
		   screenY: screenY + height / 2 + random,
		   clientX: width / 2 + random,
		   clientY: height / 2 + random
	    })
	    document.dispatchEvent(event)
    }, 1000)

/*document.addEventListener('mousemove', window);
function logKey(e) {
  console.log(`
    Screen X/Y: ${e.screenX}, ${e.screenY}
    Client X/Y: ${e.clientX}, ${e.clientY}`);
}*/

    });
</script></html>'''
        flow.response.text = flow.response.text.replace('</html>', js_one_way)
        return

    # 动态代理
    def proxy_address(self) -> typing.Tuple[str, int]:
        if self.proxy_flag:
            while True:

                self.ip = pubUtil.get_proxy().split(':')
                if len(self.ip) > 0 and len(self.ip[0]) > 0:
                    break
                time.sleep(2)
        self.proxy_flag = False

        ctx.log.info('####### ip: ' + str(self.ip))
        return (self.ip[0], int(self.ip[1]))
        # return ("127.0.0.1", 1080)
