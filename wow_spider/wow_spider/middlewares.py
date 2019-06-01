# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os
from scrapy import signals
import time,json,requests,logging,re
import logging,random,traceback,urllib
from wow_spider import settings
from wow_spider.spiders.kc import KcSpider
from wow_spider.spiders.mm import MmSpider
from wow_spider.spiders.a5j import A5jSpider
from lxml import etree
from collections import deque
from selenium import webdriver


class StatisticsItem(object):
    def __init__(self):
        self.interval = 0
        self.itemsprev = 0

    # 统计每分钟item
    def process_request(self, request, spider):
        run_time = time.time()
        if  run_time - self.interval >= 60:
            self.interval = run_time
            items = spider.crawler.stats.get_value('item_scraped_count', 0)
            irate = items - self.itemsprev
            self.itemsprev = items
            spider.crawler.stats.set_value('permins', irate)


class ProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0

    def process_request(self, request, spider):
        if hasattr(spider,'proxy') and spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)

    def _get_proxy(self, spider):
        num = spider.custom_settings.get('PROXY_TRY_NUM', 10)
        if spider.isOK:
            return self.proxy
        if self.proxyCount < num:
            self.proxyCount = self.proxyCount + 1
            logging.info('using old proxy:' + self.proxy)
            return self.proxy

        self.proxyCount = 0
        if self.backSelfCount >= 10:
            #try 10 times and back to sel ip
            logging.info('using self ip')
            self.backSelfCount = 0
            self.proxy = ''
            return self.proxy

        try:
            params = {'carrier': spider.name}
            li = json.loads(requests.get(settings.GET_PROXY_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text)
            logging.info('Proxy Num: ' + str(len(li)))
            logging.info(str(li))
            self.proxy = random.choice(li).decode('ascii') or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            # traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''


class IPV4ProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 20
        self.backSelfCount = 0

    def process_request(self, request, spider):
        if hasattr(spider, 'proxy') and spider.proxy:
            request.meta['proxy'] = 'http://' + self._get_proxy(spider)
            # print request.meta.get('proxy')

    def _get_proxy(self, spider):

        num = spider.custom_settings.get('PROXY_TRY_NUM', 10)
        if spider.isOK:
            return self.proxy
        if self.proxyCount < num:
            self.proxyCount = self.proxyCount + 1
            logging.info('using old proxy:' + self.proxy)
            return self.proxy

        self.proxyCount = 0
        if self.backSelfCount >= 10:
            # try 10 times and back to sel ip
            logging.info('using self ip')
            self.backSelfCount = 0
            self.proxy = ''
            return self.proxy

        try:
            url = settings.GET_IPV4_PROXY + spider.name
            li = json.loads(requests.get(url, timeout=settings.GET_URL_TIMEOUT).text)
            logging.info('Proxy Num: ' + str(len(li)))
            logging.info(str(li))
            self.proxy = random.choice(li).decode('ascii') or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            # traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''


class KCCookieMiddleware(object):

    def __init__(self):
        self.headers = {'Cookie':'',}
        self.cookies ={}
        self.security_hash = ''
        self.proxy = ''
        self.isOK = True

    def process_response(self, request, response, spider):
        # print('tttt')
        # spider.log(response.status, 40)
        if response.status == 302:
            spider.log('response.statuscode == 302', 40)
            return request
        return response


    def process_request(self,request,spider):
        # if not spider.isToken_cookie:
        #     self.cookies = {}
        #     self.security_hash = ''
        if not spider.isOK:
            self._get_proxy(spider)
        if not self.cookies:
            self.cookies,self.security_hash = self.get_cookies(spider)
        # request.cookies = cookies
        if not self.security_hash:
            self.headers = {'Cookie': '', }
            self.security_hash = self.get_token(spider,self.cookies)
        headers = request.headers
        headers['__securityhash'] = self.security_hash
        for k, v in self.cookies.items():
            headers['Cookie'] = headers['Cookie'] + k + '=' + v + ';'
        request.headers = headers
        if spider.proxy:
            request.meta['proxy'] = self.proxy
        # print(headers)
        # logging.info(headers)

    def get_cookies(self,spider):
        url = spider.custom_settings.get('cookie_url')[0]
        res = requests.get(url,timeout =30,verify=False,allow_redirects=False)
        cookies = res.cookies.get_dict()
        spider.log(cookies)
        # print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        securityHash = ''
        if res.status_code == 200:
            html = etree.HTML(res.text)
            securityHash = html.xpath('//*[@id="__SecurityHash"]/@value')[0]
        # else:
        #     url = spider.custom_settings.get('token_url')[0]
        #     res = requests.post(url, cookies=cookies, verify=False, timeout=30)
        #     html = etree.HTML(res.text)
        #     # print(res.text)
        #     securityHash = html.xpath('//*[@id="__SecurityHash"]/@value')[0]
        #     cookies_2 = res.cookies.get_dict()
        #     cookies = dict(cookies,**cookies_2)
        print('securityHash:' + securityHash)
        return cookies ,securityHash




    def get_token(self,spider,cookies):
        url = spider.custom_settings.get('token_url')[0]
        res = requests.post(url, cookies=cookies, verify=False, timeout=30)
        html = etree.HTML(res.text)
        # print(res.text)
        securityHash = html.xpath('//*[@id="__SecurityHash"]/@value')[0]
        # logging.info('hash:' + SecurityHash)
        print(securityHash)
        return securityHash


    def _get_proxy(self, spider):
        if not hasattr(spider, 'proxy') or not spider.proxy:
            return ''
        print('update proxy')
        try:
            params = {'carrier': spider.name}
            li = json.loads(requests.get(settings.GET_PROXY_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text)
            logging.info('Proxy Num: ' + str(len(li)))
            logging.info(str(li))
            self.proxy = random.choice(li).decode('ascii') or ''
        except:
            traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''


class MMProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0
        self.proxy_num = 0

    def process_request(self, request, spider):
        if spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)
            self.proxy_num += 1
        if self.proxy_num == 6:
            self.proxy_num = 0

    def _get_proxy(self, spider):
        if spider.isOK:
            return self.proxy
        if self.proxy_num > 1:
            return self.proxy

        ip_port = spider.custom_settings.get('IP_PROXY')
        ip_url = spider.custom_settings.get('IP_URL')
        num = str(random.randint(200,1000))
        ip_port = ip_port%num
        proxies = {
            'http': ip_port,
            'https': ip_port
        }
        self.proxy =ip_port
        try:
            html_source = requests.get(ip_url, proxies=proxies).text
            # html_source = requests.get('http://httpbin.org/ip', proxies=proxies).text
            # print(html_source)
            ip = re.search(r'":"(.*?)","country', html_source).group(1)
            print('update proxy:%s'%ip)
            return self.proxy or ''
        except:
            # traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''


class MMcookieMiddleware(object):
    def __init__(self):
        self.cookie = '3889838004566105755661057'
        self.cookie_num = 0

    def process_request(self,request,spider):

        if not spider.isCOOKIE:
            self.cookie = self.get_cookie(spider)
        if self.cookie_num == 3:
            self.cookie = self.get_cookie(spider)
            self.cookie_num =0
            # self.cookie = '3889838004566105755661057'
        headers = request.headers
        headers['Cookie'] = '__z_a=' + self.cookie + ';'
        self.cookie_num +=1
        # for k, v in self.cookies.items():
        #     headers['Cookie'] = headers['Cookie'] + k + '=' + v + ';'
        request.headers = headers
        # print(headers['Cookie'])


    def get_cookie(self,spider):
        cookie_url = spider.custom_settings.get('COOKIE_URL')
        cookie_payload = spider.custom_settings.get('COOKIE_PAYLOAD')
        cookie_headers = spider.custom_settings.get('COOKIE_HEADERS')
        cookie_timeout = spider.custom_settings.get('DOWNLOAD_TIMEOUT')
        size = '%sx%s' % (random.randint(200, 1000), random.randint(200, 1000))
        cookie_payload.update(dict(
            ScreenResolution=size,
            AvailableScreenResolution=size,
        )
        )
        payload = 'data=%s' % json.dumps(cookie_payload)
        try:
            response = requests.request("POST", cookie_url, data=payload, headers=cookie_headers,verify=False,timeout=cookie_timeout)
            # print('updata cookie:' + response.text)
            print('update cookie:' + response.text)
            return response.text
        except:
            traceback.print_exc()
            return ''
        # print('----------------------------------')


class a5JtokenMiddleware(object):

    def __init__(self):
        self.token =''
        self.token_num = 0
        self.queue = deque(maxlen=10)

    def process_request(self, request, spider):
        if not spider.isOK:
            self.token = self.get_token(spider)
            self.token_num +=1
        if self.token_num == 3:
            self.token_num = 0
        headers = request.headers
        headers['authorization'] = self.token
        request.headers = headers

    def get_token(self,spider):
        if self.token_num >1:
            return self.token
        token_url = spider.custom_settings.get('TOKEN_URL')
        token_payload = ''
        token_headers = spider.custom_settings.get('HEADERS')
        token_timeout = spider.custom_settings.get('DOWNLOAD_TIMEOUT')
        try:
            res = requests.post(token_url,headers=token_headers,data=token_payload,verify=False,timeout=token_timeout)
            data = json.loads(res.text)
            token = data.get('data').get('token')
            print("update token:%s"%token)
            self.queue.append(token)
            return token
        except:
            # traceback.print_exc()
            print("get token error,back up")
            if len(self.queue) == 0:
                token = ''
            else:
                # print(self.queue)
                token =self.queue.popleft()
                if len(self.queue) < 5:
                    self.queue.append(token)
            return token

            # time.sleep(5)
            # self.get_token(spider)


class XQSessionMiddleware(object):
    def __init__(self):
        pass

    # def process_response(self, request, response, spider):
    #     print(response.text)
    #     if response.status != 200:
    #         logging.info('response error,  Change ip')
    #         self.isOK = False
    #         return request
    #     self.isOK = True
    #     return response

    def process_request(self, request, spider):
        session = self.get_session_id(spider)
        request._set_url(request.url + session)
        # print(request._set_url)

    def get_session_id(self,spider):
        session_url = spider.custom_settings.get('SESSION_ID_URL')
        session_header = spider.custom_settings.get('HEADERS')

        try:
            response = requests.request("GET", session_url, headers=session_header, verify=False,timeout=spider.custom_settings.get('DOWNLOAD_TIMEOUT'))
            html = etree.HTML(response.text)
            href = html.xpath('//*[@id="command"]/@action')[0]
            # print(href)
            return href
        except:
            traceback.print_exc()
            print('get session error')
            return ''


class FIJsMiddleware(object):
    def __init__(self):
        self.js_num = 0
        self.cookies ={'D_ZID': '2D97761B-571B-3DC3-BC4F-4FADE86A25A1', 'D_IID': 'F715DA45-7692-39C1-BE92-2266DFFC637C', 'D_ZUID': '85280F0F-D383-319D-8DD7-F98182CF46D6', 'D_UID': 'F7C1C238-A0FC-308C-9EEE-528CC2CF8F65', 'D_HID': '4834BC84-D885-3395-88A7-AE62D771CF2A'}

    def process_request(self, request, spider):
        if not spider.isJS:
            self.cookies = self.get_js(spider)
            self.js_num += 1
        if self.js_num == 5:
            self.js_num = 0
        headers = request.headers
        # print(self.cookies)
        # print('2' * 44)
        # print(self.cookies)
        for k, v in self.cookies.items():
            headers['Cookie'] = headers['Cookie'] + k + '=' + v + ';'
        request.headers = headers
        # print('1'*44)

    def get_js(self,spider):
        if self.js_num > 1:
            return self.cookies
        js_url = spider.custom_settings.get('JS_URL')
        js_random_postfix = spider.custom_settings.get('JS_RANDOM_POSTFIX')
        url = js_url +js_random_postfix
        js_header1 = spider.custom_settings.get('JS_HEADER1')
        js_header2 = spider.custom_settings.get('JS_HEADER2')
        token_timeout = spider.custom_settings.get('DOWNLOAD_TIMEOUT')
        querystring = {"PID": "EC412E1F-C8F4-3AA3-B67B-48A1565D374B"}
        data = 'p=%7B%22proof%22%3A%228%3A1537436897277%3AblG8djax1lRLmRfyt9Sq%22%2C%22fp2%22%3A%7B%22userAgent%22%3A%22Mozilla%2F5.0(WindowsNT10.0%3BWOW64)AppleWebKit%2F537.36(KHTML%2ClikeGecko)Chrome%2F68.0.3440.106Safari%2F537.36%22%2C%22language%22%3A%22zh-CN%22%2C%22screen%22%3A%7B%22width%22%3A1920%2C%22height%22%3A1080%2C%22availHeight%22%3A1040%2C%22availWidth%22%3A1920%2C%22pixelDepth%22%3A24%2C%22innerWidth%22%3A958%2C%22innerHeight%22%3A943%2C%22outerWidth%22%3A1920%2C%22outerHeight%22%3A1040%2C%22devicePixelRatio%22%3A1%7D%2C%22timezone%22%3A8%2C%22indexedDb%22%3Atrue%2C%22addBehavior%22%3Afalse%2C%22openDatabase%22%3Atrue%2C%22cpuClass%22%3A%22unknown%22%2C%22platform%22%3A%22Win32%22%2C%22doNotTrack%22%3A%22unknown%22%2C%22plugins%22%3A%22ChromePDFPlugin%3A%3APortableDocumentFormat%3A%3Aapplication%2Fx-google-chrome-pdf~pdf%3BChromePDFViewer%3A%3A%3A%3Aapplication%2Fpdf~pdf%3BNativeClient%3A%3A%3A%3Aapplication%2Fx-nacl~%2Capplication%2Fx-pnacl~%22%2C%22canvas%22%3A%7B%22winding%22%3A%22yes%22%2C%22towebp%22%3Atrue%2C%22blending%22%3Atrue%2C%22img%22%3A%22627c71c66e734317ee2072e5bc9a9a942b8f4cf6%22%7D%2C%22webGL%22%3A%7B%22img%22%3A%22bd6549c125f67b18985a8c509803f4b883ff810c%22%2C%22extensions%22%3A%22ANGLE_instanced_arrays%3BEXT_blend_minmax%3BEXT_color_buffer_half_float%3BEXT_frag_depth%3BEXT_shader_texture_lod%3BEXT_texture_filter_anisotropic%3BWEBKIT_EXT_texture_filter_anisotropic%3BEXT_sRGB%3BOES_element_index_uint%3BOES_standard_derivatives%3BOES_texture_float%3BOES_texture_float_linear%3BOES_texture_half_float%3BOES_texture_half_float_linear%3BOES_vertex_array_object%3BWEBGL_color_buffer_float%3BWEBGL_compressed_texture_s3tc%3BWEBKIT_WEBGL_compressed_texture_s3tc%3BWEBGL_compressed_texture_s3tc_srgb%3BWEBGL_debug_renderer_info%3BWEBGL_debug_shaders%3BWEBGL_depth_texture%3BWEBKIT_WEBGL_depth_texture%3BWEBGL_draw_buffers%3BWEBGL_lose_context%3BWEBKIT_WEBGL_lose_context%22%2C%22aliasedlinewidthrange%22%3A%22%5B1%2C1%5D%22%2C%22aliasedpointsizerange%22%3A%22%5B1%2C1024%5D%22%2C%22alphabits%22%3A8%2C%22antialiasing%22%3A%22yes%22%2C%22bluebits%22%3A8%2C%22depthbits%22%3A24%2C%22greenbits%22%3A8%2C%22maxanisotropy%22%3A16%2C%22maxcombinedtextureimageunits%22%3A32%2C%22maxcubemaptexturesize%22%3A16384%2C%22maxfragmentuniformvectors%22%3A1024%2C%22maxrenderbuffersize%22%3A16384%2C%22maxtextureimageunits%22%3A16%2C%22maxtexturesize%22%3A16384%2C%22maxvaryingvectors%22%3A30%2C%22maxvertexattribs%22%3A16%2C%22maxvertextextureimageunits%22%3A16%2C%22maxvertexuniformvectors%22%3A4096%2C%22maxviewportdims%22%3A%22%5B16384%2C16384%5D%22%2C%22redbits%22%3A8%2C%22renderer%22%3A%22WebKitWebGL%22%2C%22shadinglanguageversion%22%3A%22WebGLGLSLES1.0(OpenGLESGLSLES1.0Chromium)%22%2C%22stencilbits%22%3A0%2C%22vendor%22%3A%22WebKit%22%2C%22version%22%3A%22WebGL1.0(OpenGLES2.0Chromium)%22%2C%22vertexshaderhighfloatprecision%22%3A23%2C%22vertexshaderhighfloatprecisionrangeMin%22%3A127%2C%22vertexshaderhighfloatprecisionrangeMax%22%3A127%2C%22vertexshadermediumfloatprecision%22%3A23%2C%22vertexshadermediumfloatprecisionrangeMin%22%3A127%2C%22vertexshadermediumfloatprecisionrangeMax%22%3A127%2C%22vertexshaderlowfloatprecision%22%3A23%2C%22vertexshaderlowfloatprecisionrangeMin%22%3A127%2C%22vertexshaderlowfloatprecisionrangeMax%22%3A127%2C%22fragmentshaderhighfloatprecision%22%3A23%2C%22fragmentshaderhighfloatprecisionrangeMin%22%3A127%2C%22fragmentshaderhighfloatprecisionrangeMax%22%3A127%2C%22fragmentshadermediumfloatprecision%22%3A23%2C%22fragmentshadermediumfloatprecisionrangeMin%22%3A127%2C%22fragmentshadermediumfloatprecisionrangeMax%22%3A127%2C%22fragmentshaderlowfloatprecision%22%3A23%2C%22fragmentshaderlowfloatprecisionrangeMin%22%3A127%2C%22fragmentshaderlowfloatprecisionrangeMax%22%3A127%2C%22vertexshaderhighintprecision%22%3A0%2C%22vertexshaderhighintprecisionrangeMin%22%3A31%2C%22vertexshaderhighintprecisionrangeMax%22%3A30%2C%22vertexshadermediumintprecision%22%3A0%2C%22vertexshadermediumintprecisionrangeMin%22%3A31%2C%22vertexshadermediumintprecisionrangeMax%22%3A30%2C%22vertexshaderlowintprecision%22%3A0%2C%22vertexshaderlowintprecisionrangeMin%22%3A31%2C%22vertexshaderlowintprecisionrangeMax%22%3A30%2C%22fragmentshaderhighintprecision%22%3A0%2C%22fragmentshaderhighintprecisionrangeMin%22%3A31%2C%22fragmentshaderhighintprecisionrangeMax%22%3A30%2C%22fragmentshadermediumintprecision%22%3A0%2C%22fragmentshadermediumintprecisionrangeMin%22%3A31%2C%22fragmentshadermediumintprecisionrangeMax%22%3A30%2C%22fragmentshaderlowintprecision%22%3A0%2C%22fragmentshaderlowintprecisionrangeMin%22%3A31%2C%22fragmentshaderlowintprecisionrangeMax%22%3A30%7D%2C%22touch%22%3A%7B%22maxTouchPoints%22%3A0%2C%22touchEvent%22%3Afalse%2C%22touchStart%22%3Afalse%7D%2C%22video%22%3A%7B%22ogg%22%3A%22probably%22%2C%22h264%22%3A%22probably%22%2C%22webm%22%3A%22probably%22%7D%2C%22audio%22%3A%7B%22ogg%22%3A%22probably%22%2C%22mp3%22%3A%22probably%22%2C%22wav%22%3A%22probably%22%2C%22m4a%22%3A%22maybe%22%7D%2C%22vendor%22%3A%22GoogleInc.%22%2C%22product%22%3A%22Gecko%22%2C%22productSub%22%3A%2220030107%22%2C%22browser%22%3A%7B%22ie%22%3Afalse%2C%22chrome%22%3Atrue%2C%22webdriver%22%3Afalse%7D%2C%22window%22%3A%7B%22historyLength%22%3A39%2C%22hardwareConcurrency%22%3A8%2C%22iframe%22%3Afalse%7D%2C%22fonts%22%3A%22Calibri%3BCentury%3BMarlett%3BPristina%3BSimHei%22%7D%2C%22cookies%22%3A1%2C%22setTimeout%22%3A0%2C%22setInterval%22%3A0%2C%22appName%22%3A%22Netscape%22%2C%22platform%22%3A%22Win32%22%2C%22syslang%22%3A%22zh-CN%22%2C%22userlang%22%3A%22zh-CN%22%2C%22cpu%22%3A%22%22%2C%22productSub%22%3A%2220030107%22%2C%22plugins%22%3A%7B%220%22%3A%22ChromePDFPlugin%22%2C%221%22%3A%22ChromePDFViewer%22%2C%222%22%3A%22NativeClient%22%7D%2C%22mimeTypes%22%3A%7B%220%22%3A%22application%2Fpdf%22%2C%221%22%3A%22PortableDocumentFormatapplication%2Fx-google-chrome-pdf%22%2C%222%22%3A%22NativeClientExecutableapplication%2Fx-nacl%22%2C%223%22%3A%22PortableNativeClientExecutableapplication%2Fx-pnacl%22%7D%2C%22screen%22%3A%7B%22width%22%3A1920%2C%22height%22%3A1080%2C%22colorDepth%22%3A24%7D%2C%22fonts%22%3A%7B%220%22%3A%22Calibri%22%2C%221%22%3A%22Cambria%22%2C%222%22%3A%22Times%22%2C%223%22%3A%22Constantia%22%2C%224%22%3A%22Georgia%22%2C%225%22%3A%22SegoeUI%22%2C%226%22%3A%22Candara%22%2C%227%22%3A%22TrebuchetMS%22%2C%228%22%3A%22Verdana%22%2C%229%22%3A%22Consolas%22%2C%2210%22%3A%22LucidaConsole%22%2C%2211%22%3A%22CourierNew%22%2C%2212%22%3A%22Courier%22%7D%7D'

        try:
            res = requests.get(url,headers=js_header1,verify=False,timeout=token_timeout)
            # print(url)
            # print('6'*88)
            res = requests.post(url,headers=js_header2,data=data,params=querystring,verify=False,timeout=token_timeout)
            # data = json.loads(res.text)
            # token = data.get('data').get('token')
            print("update js")
            cookies = res.cookies.get_dict()
            print(cookies)
            if not cookies:
                print('1'*44)
                cookies = self.cookies

            return cookies
        except:
            # traceback.print_exc()
            print("get js error,back up")

            return self.cookies


class A4OTokenMiddleware(object):
    def __init__(self):
        self.token = None

    def process_request(self, request, spider):
        if not self.token:
            self.token = self.get_token(request,spider)
        if not self.token:
            spider.isOK = False
            return request
        request._set_url(request.url + "Signature="+urllib.quote(self.token))

    def get_token(self, request, spider):
        token_url = spider.custom_settings.get('TOKEN_URL')
        token_headers = spider.custom_settings.get('HEADERS')
        token_headers['User-Agent'] = spider.ua_construction()
        # print 'token_headers:' ,token_headers['User-Agent']
        token_timeout = spider.custom_settings.get('DOWNLOAD_TIMEOUT')
        proxy = request.meta.get('proxy')
        proxies = {
            'http': 'http://%s'%proxy,
            'https': 'https://%s'%proxy
        }
        try:
            res = requests.get(token_url,headers=token_headers,proxies=proxies,verify=False,timeout=token_timeout)
            data = json.loads(res.text)
            token = data.get('Signature')
            print("update token:%s"%token)
            return token
        except:
            # traceback.print_exc()
            print("get token error,back up")
            return self.token

            # time.sleep(5)
            # self.get_token(spider)


class BJCookieMiddleware(object):
    def __init__(self):
        self.cookie = None

    def process_request(self, request, spider):
        # if not self.token:
        #     self.token = self.get_token(spider)
        # request._set_url(request.url + "Signature="+urllib.quote(self.token))
        headers = request.headers
        # print(self.cookies)
        # print('2' * 44)
        # print(self.cookies)
        if self.cookie:
            headers['Cookie'] = headers['Cookie'] + "JSESSIONID=" + self.cookie + ';'
        request.headers = headers

    def process_response(self, request, response, spider):
        if not self.cookie:
            self.cookie = self.get_cookie(spider,response)
        return response

    def get_cookie(self, spider,response):
        setcookie = response.headers.get("Set-Cookie").split(';')
        cookie_dict = {}
        # print setcookie,'6'*66
        for cookie in setcookie:
            c = cookie.split('=')
            if len(c) == 1:
                c = [c[0],'']
            cookie_dict[c[0]] = c[1]
        return cookie_dict.get("JSESSIONID",None)


class TRMiddleware(object):
    def __init__(self):
        self.url = 'https://www.wxflyscoot.com/home/booking/select'
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-cn',
            'Connection': 'keep-alive',
            'Host': 'www.wxflyscoot.com',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 10_3_3 like Mac OS X) AppleWebKit/603.3.8 (KHTML, like Gecko) Mobile/14G60 MicroMessenger/7.0.1(0x17000120) NetType/WIFI Language/zh_CN'
        }

    def process_request(self, request, spider):
        pass

    def process_response(self, request, response, spider):
        timeout = spider.custom_settings.get('DOWNLOAD_TIMEOUT')
        if response.status == 200:
            try:
                self.headers['Cookie'] = request.headers.get('Cookie')
                res = requests.get(self.url, headers=self.headers, verify=False, timeout=timeout)
                # 因为需要二次请求，我把第二次请求放在这里进行操作
                # scrapy不支持返回非scrapy response的数据，因此把res的数据放入meta中
                request.meta['response'] = res
                return response
            except:
                traceback.print_exc()
                print 'select获取数据错误，可能cookie失效'
        else:
            print 'ajax获取数据错误，可能cookie失效'

        return response


class A9CJSMiddleware(object):
    def __init__(self):
        self.cookie = '5c6a5116e4b0d722d67fefe32aae952126c63faa'
        self.connection = True

    def process_request(self, request, spider):
        request.headers['Cookie'] = "acw_sc__v2=" + self.cookie + ';'
        if not self.connection:
            request.headers.pop('Connection')
            request.headers['Connection'] = "close"
        self.connection = True

    def process_response(self, request, response, spider):
        if response.text.find('{') == 0:
            return response
        print '1'*66
        print response.text
        num_front = response.text.find('var arg1=')
        num_back = response.text.find('function setCookie')
        js_data = r'' + response.text[num_front:num_back]
        html_content = r"""<html><script>
        """ + js_data + r"""
        function html(x) {
            return html = '<div>' + x + '</div>';
        }
        function setCookie(name,value){var expiredate=new Date();expiredate.setTime(expiredate.getTime()+(3600*1000));document.cookie=name+"="+value+";expires="+expiredate.toGMTString()+";max-age=3600;path=/";}
        function reload(x) {document.body.insertAdjacentHTML('afterbegin', html(x));}
        </script></html>"""

        driver = webdriver.Chrome()
        with open('utils/a9c_js.html', 'w') as f:
            f.write(html_content)
        try:
            driver.get("file:///" + os.path.abspath('utils/a9c_js.html'))
            time.sleep(5)
            self.cookie = driver.find_element_by_xpath('/html/body/div').text
            print '更新cookie：', self.cookie
        except:
            print('重启错误，关闭连接再试')
            self.connection = False
        driver.close()
        # time.sleep(30)
        return request