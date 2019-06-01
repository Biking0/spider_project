# -*- coding: utf-8 -*-
from six.moves.urllib.parse import urljoin
from w3lib.url import safe_url_string

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time, logging, random, requests, json, traceback
from fake_useragent import UserAgent
from scrapy import signals
from scrapy.http.response.html import HtmlResponse
import os, re
from lamudatech_dev import settings
from utils.process_cookies.u2_cookies import get_cookies

try:
    from urllib import parse
except ImportError:
    import urllib as parse


def _get_proxy(spider):
    if spider.proxy:
        proxy_url = spider.settings.get('PROXY_URL') + spider.spider_name
        res = requests.get(proxy_url)
        proxies_list = json.loads(res.text)
        proxy = random.choice(proxies_list)
        spider.log('\t get proxy: %s' % proxy, 20)
    else:
        proxy = None
    return proxy


class CookiesBase(object):
    def __init__(self):
        self.firefox_options = webdriver.FirefoxOptions()
        # self.firefox_options.add_argument('-headless')
        self.firefox_profile = webdriver.FirefoxProfile()
        # 不加载图片
        # self.firefox_profile.set_preference('permissions.default.image', 2)
        # 禁用webRTC
        self.firefox_profile.set_preference("media.peerconnection.enabled", False)
        self.proxy = None
        self.driver = None

    def init_browser(self, spider):
        spider.log('browser initialize...', 20)
        if self.proxy:
            ip, port = self.proxy.split(':')
            port = int(port)
            spider.log(self.proxy, 20)
            self.firefox_profile.set_preference('network.proxy.type', 1)
            self.firefox_profile.set_preference('network.proxy.http', ip)
            self.firefox_profile.set_preference('network.proxy.http_port', port)
            self.firefox_profile.set_preference('network.proxy.ssl', ip)
            self.firefox_profile.set_preference('network.proxy.ssl_port', port)
            self.firefox_profile.set_preference('network.proxy.socks', ip)
            self.firefox_profile.set_preference('network.proxy.socks_port', port)
            self.firefox_profile.set_preference('network.proxy.ftp', ip)
            self.firefox_profile.set_preference('network.proxy.ftp_port', port)

        self.driver = webdriver.Firefox(
            firefox_options=self.firefox_options,
            firefox_profile=self.firefox_profile,
            log_path=os.devnull
        )


class UserAgentMiddleware(object):
    def __init__(self):
        self.ua = UserAgent()

    def process_request(self, request, spider):
        request.headers.setdefault('User-Agent', self.ua.random)


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


class VjProxyMiddleware(object):
    def __init__(self):
        self.now = 0
        self.isOK = True
        self.proxyCount = 0
        self.backSelfCount = 0
        self.proxy = ''

    def process_response(self, request, response, spider):
        if response.status == 403 or response.status == 504:
            self.isOK = False
            logging.info('403 Error, pls change IP')
            return request
        self.isOK = True
        return response

    def process_request(self, request, spider):
        if hasattr(spider, 'proxy') and spider.proxy:
            request.meta["proxy"] = self._get_proxy(spider)

    def _get_proxy(self, spider):
        if self.isOK and spider.is_ok:
            self.proxyCount = 0
            return self.proxy
        if self.proxyCount < 4:
            self.proxyCount = self.proxyCount + 1
            # print('proxyCount: %s' % self.proxyCount)
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
            li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=vj').text)
            logging.info('Proxy Num: ' + str(len(li)))
            logging.info(str(li))
            self.proxy = random.choice(li).decode('ascii') or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''

class ProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0

    def process_request(self, request, spider):
        if spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)

    def _get_proxy(self, spider):
        if spider.is_ok:
            return self.proxy
        if self.proxyCount < 3:
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
            traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''


class U2ProcessCookies(object):
    def __init__(self):
        self.cookies = ''
        self.proxy = ''
        self.is_ok = False
        self.proxyCount = 0
        self.backSelfCount = 0

    def is_need_proxy(self, host_name):
        if host_name.startswith('vt') or host_name.startswith('wc'):
            return False
        return True

    def process_response(self, request, response, spider):
        if response.status == 403:
            spider.log('403 Change Cookie \nSleep...', 40)
            self.cookies = self._get_cookies(spider)
            if self.is_need_proxy(spider.host_name):
                self.is_ok = False
            return request
        elif response.status != 200:
            spider.log('err_status: %s' % response.status, 20)
            if self.is_need_proxy(spider.host_name):
                self.is_ok = False
                return request
        self.is_ok = True
        return response

    def process_request(self, request, spider):
        if not self.cookies:
            self.cookies = self._get_cookies(spider)
        if hasattr(spider, 'proxy') and spider.proxy:
            request.meta["proxy"] = self._get_proxy(spider)

        request.cookies = self.cookies
        spider.is_ok = True

    def _get_cookies(self, spider=None):
        while True:
            cookies = get_cookies(spider)
            if cookies:
                spider.log('got cookies', 20)
                return cookies
            else:
                if self.cookies:
                    return self.cookies
            time.sleep(10)

    def _get_proxy(self, spider):
        if spider.is_ok and self.is_ok:
            return self.proxy
        if self.proxyCount < 2:
            self.proxyCount = self.proxyCount + 1
            logging.info('using old proxy:' + self.proxy)
            return self.proxy

        self.proxyCount = 0
        if self.backSelfCount >= 40:
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
            traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''




class LxProcessCookies(CookiesBase):
    def __init__(self):
        super(LxProcessCookies, self).__init__()
        self.num = 1

    def process_request(self, request, spider):
        if spider.name == 'lx' and 'origin' in request.meta:
            while True:
                # 初始化浏览器
                if not self.driver:
                    self.init_browser(spider)
                try:
                    # 模拟请求初始页
                    self.driver.get(request.url)

                    if 'Schedule'in self.driver.current_url:
                        print('这条路线与其他航空公司一起提供。')
                        return None
                    if 'False' in self.driver.current_url:
                        print('我们无法找到所选路线的航班。')
                        return None
                    if 'distil_r_captcha' in self.driver.current_url:
                        spider.log('验证码出现，换ip,,,,,,')
                        if spider.proxy:
                            self.proxy = _get_proxy(spider)
                    # 等待数据
                    WebDriverWait(self.driver, 50).until(
                        EC.presence_of_element_located(
                            (By.ID, 'frm-matrix')
                    ))
                except:
                    spider.log('browser error, 8 seconds after the restart.', 40)
                    spider.log('exception ,change proxy....')
                    if spider.proxy:
                        self.proxy = _get_proxy(spider)
                    # traceback.print_exc()
                    try:
                        self.driver.close()
                        self.driver = None
                    except:
                        self.driver = None
                    time.sleep(8)
                else:
                    break

            # 自定义Response对象
            current_url = bytes(self.driver.current_url)
            body = bytes(self.driver.page_source.encode('utf-8'))
            response = HtmlResponse(current_url, body=body)

            # 设置cookies
            if spider.proxy:
                request.meta["proxy"] = self.proxy
            request.cookies = self.driver.get_cookies()

            # 设置headers
            request.headers.setdefault('Referer', current_url)

            # 清除cookies
            self.driver.delete_all_cookies()
            spider.log('delete_all_cookies', 20)
            # 暂停爬虫引擎
            # spider.crawler.engine.pause()

            # 注释掉以后不再关闭浏览器
            if self.num % 6 == 0:
                spider.log('browser closed.', 20)
                self.driver.close()
                self.driver = None
            self.num += 1

            return response
        elif not spider.is_ok and spider.proxy:
            self.proxy = _get_proxy(spider)


class EwProcessCookies(object):
    def process_response(self, request, response, spider):
        if response.status == 302:
            set_cookies = response.headers.getlist('Set-Cookie')
            cookie_items = [re.match(r'(.*?)=(.*?);', i).groups() for i in set_cookies]
            cookies = [{u'domain': u'.eurowings.com', u'secure': False, u'value': unicode(v), u'expiry': None,
                        u'path': u'/', u'httpOnly': False, u'name': unicode(k)} for k, v in cookie_items]
            request.cookies = cookies

            location = safe_url_string(response.headers['location'])
            redirected_url = urljoin(request.url, location)
            redirected = self._redirect_request_using_get(request, redirected_url)
            return self._redirect(redirected, request, spider, response.status)
        return response

    def _redirect(self, redirected, request, spider, reason):
        ttl = request.meta.setdefault('redirect_ttl', spider.settings.getint('REDIRECT_MAX_TIMES'))
        redirects = request.meta.get('redirect_times', 0) + 1

        if ttl and redirects <= spider.settings.getint('REDIRECT_MAX_TIMES'):
            redirected.meta['redirect_times'] = redirects
            redirected.meta['redirect_ttl'] = ttl - 1
            redirected.meta['redirect_urls'] = request.meta.get('redirect_urls', []) + \
                [request.url]
            redirected.dont_filter = request.dont_filter
            redirected.priority = request.priority + spider.settings.getint('REDIRECT_PRIORITY_ADJUST')
            return redirected

    def _redirect_request_using_get(self, request, redirect_url):
        redirected = request.replace(url=redirect_url, method='GET', body='')
        redirected.headers.pop('Content-Type', None)
        redirected.headers.pop('Content-Length', None)
        return redirected


class UoProcessCookies(CookiesBase):
    def __init__(self):
        super(UoProcessCookies, self).__init__()
        self.num = 1

    def process_request(self, request, spider):
        if spider.name == 'uo' and 'origin' in request.meta and request.meta['origin'] == 1:

            meta = request.meta
            _from = meta['_from']
            _to = meta['_to']

            while True:
                # 初始化浏览器
                if not self.driver:
                    self.init_browser(spider)
                try:
                    # 模拟请求初始页
                    self.driver.get(request.url)

                    # 处理滑块验证码
                    if u"Please slide to verify that you're not a robot" in self.driver.page_source:
                        self.driver.maximize_window()
                        action = ActionChains(self.driver)
                        fuck = self.driver.find_element_by_id('nc_1_n1z')
                        action.drag_and_drop_by_offset(fuck, 233.51, 0).perform()

                        spider.log("Please slide to verify that you're not a robot", 40)
                        self.driver.delete_all_cookies()
                        try:
                            self.driver.close()
                            self.driver = None
                        except:
                            self.driver = None
                        time.sleep(8)
                        continue

                    else:
                        # Ajax请求
                        comment = '''var data=%s;
                           $.post("#", data, function(){
                           window.location.href = "/en-US/select?origin=%s&amp;destination=%s"
                           })''' % (request.body, _from, _to)
                        self.driver.execute_script(comment)

                        # 等待数据
                        WebDriverWait(self.driver, 50).until(
                            EC.presence_of_element_located(
                                (By.XPATH, '//*[@name="__RequestVerificationToken"]')
                            ))
                        break
                except:
                    traceback.print_exc()
                    spider.log('browser error, 8 seconds after the restart.', 40)
                    try:
                        self.driver.close()
                        self.driver = None
                    except:
                        self.driver = None
                    time.sleep(8)

            # 自定义Response对象
            current_url = bytes(self.driver.current_url)
            body = bytes(self.driver.page_source.encode('utf-8'))
            response = HtmlResponse(current_url, body=body)

            # 设置cookies
            request.cookies = self.driver.get_cookies()

            # 设置headers
            request.headers.setdefault('Referer', current_url)

            # 注释掉以后不再关闭浏览器
            if self.num % 10 == 0:
                spider.log('browser closed.', 20)
                self.driver.close()
                self.driver = None

            self.num += 1

            # 清除cookies
            spider.log('delete_all_cookies', 20)
            self.driver.delete_all_cookies()
            return response


class LjProcessCookies(object):
    def __init__(self):
        self.index_url = 'https://www.jinair.com/booking/index'
        self.cookies = None
        self.csrf_token = None

    def process_response(self, request, response, spider):
        if response.status == 403:
            spider.log('%s Change Cookie \nSleep...' % response.status, 40)
            spider.change_cookies = True
            return request
        return response

    def process_request(self, request, spider):
        if self.cookies is None or spider.change_cookies is True:
            spider.change_cookies = False
            self.cookies, self.csrf_token = self._get_cookies()
        request.headers.update({'x-csrf-token': self.csrf_token})
        request.cookies = self.cookies

    def _get_cookies(self):
        headers = {
            'referer': "https://www.jinair.com",
            'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.162 Safari/537.36",
            'Cache-Control': "no-cache"
        }
        while True:
            try:
                response = requests.get(self.index_url, headers=headers, timeout=180)
                break
            except Exception as e:
                traceback.print_exc()
                time.sleep(8)

        set_cookies = response.headers['Set-Cookie']
        session_id = re.match(r'JSESSIONID=(.*?);', set_cookies).group(1)
        pattern = re.compile(r'.*key=X-CSRF-TOKEN&val=(.*?)"', flags=re.DOTALL)
        csrf_token = pattern.match(response.text).group(1)
        cookies = []
        cookies.extend([
            {u'domain': u'www.jinair.com', u'secure': False, u'value': unicode(session_id), u'expiry': None,
             u'path': u'/', u'httpOnly': False, u'name': u'JSESSIONID'},
            {u'domain': u'.jinair.com', u'secure': False, u'value': u'CHN', u'expiry': None, u'path': u'/',
             u'httpOnly': False, u'name': u'foCountry'},
            {u'domain': u'.jinair.com', u'secure': False, u'value': u'CN', u'expiry': None, u'path': u'/',
             u'httpOnly': False, u'name': u'foPop'},
            {u'domain': u'.jinair.com', u'secure': False, u'value': u'CHN', u'expiry': None, u'path': u'/',
             u'httpOnly': False, u'name': u'foLangCd'},
            {u'domain': u'.jinair.com', u'secure': False, u'value': u'zh-Hans', u'expiry': None, u'path': u'/',
             u'httpOnly': False, u'name': u'foLang'},
            {u'domain': u'.jinair.com', u'secure': False, u'value': u'zh_CN', u'expiry': None, u'path': u'/',
             u'httpOnly': False, u'name': u'foLangCountry'}
        ])

        return cookies, csrf_token


class AkProcessCookies(CookiesBase):
    def __init__(self):
        super(AkProcessCookies, self).__init__()
        self.cookies = None
        self.run_time = 0
        self.num = 1

    def process_response(self, request, response, spider):
        if response.status != 200:
            spider.errback_status = True
            return request
        else:
            return response

    def process_request(self, request, spider):
        if 'origin' in request.meta or spider.errback_status is True:
            while True:
                # 每隔10分钟设置代理为None
                now = time.time()
                if now - self.run_time > 60 * 10:
                    self.close_err_driver(spider, 'set proxy is None')
                    self.proxy = None
                    self.run_time = now
                # 初始化浏览器
                if not self.driver:
                    self.init_browser(spider)
                try:
                    # 模拟请求初始页
                    self.driver.get(request.url)

                    if 'err504' in self.driver.current_url:
                        self.close_err_driver(spider, 'page err504')
                        # 更换代理
                        self.proxy = _get_proxy(spider)
                        continue
                    # 等待数据
                    WebDriverWait(self.driver, 40).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="availabilityForm"]')
                        ))
                except:
                    traceback.print_exc()
                    # 更换代理
                    self.proxy = _get_proxy(spider)
                    self.close_err_driver(spider, 'browser error, 3 seconds after the restart.')
                else:
                    break

            # 设置cookies
            self.cookies = self.driver.get_cookies()
            request.cookies = self.cookies
            request.meta['proxy'] = self.proxy

            # 清除cookies
            spider.log('delete_all_cookies', 20)
            self.driver.delete_all_cookies()

            # 自定义Response对象
            current_url = bytes(self.driver.current_url)
            body = bytes(self.driver.page_source.encode('utf-8'))
            response = HtmlResponse(current_url, body=body, request=request)

            # # 注释掉以后不再关闭浏览器
            # if self.num % 6 == 0:
            #     spider.log('browser closed.', 20)
            #     self.driver.close()
            #     self.driver = None
            #
            # self.num += 1

            spider.errback_status = False
            return response
        else:
            request.meta['proxy'] = self.proxy
            request.cookies = self.cookies

    def close_err_driver(self, spider, msg):
        try:
            self.driver.close()
        except:
            pass
        finally:
            spider.log(msg, 20)
            self.driver = None
            time.sleep(3)


class A5jProcessCookies:
    def __init__(self):
        self.run_time = 0
        self.cookies = None
        self.tracking_id = None
        self.token_15m = None

    def process_response(self, request, response, spider):
        if response.status == 429:
            spider.err_429 = True
            return request
        return response

    def process_request(self, request, spider):
        now = time.time()
        if spider.err_429 is True or now - self.run_time > 60 * 10:
            self.run_time = now
            self.token_15m, self.cookies, self.tracking_id = self._get_token(spider)

        request.headers.update({'loggly-tracking-id': self.tracking_id,
                                'Authorization': self.token_15m})
        request.cookies = self.cookies
        spider.err_429 = False

    def _get_token(self, spider):
        url = 'https://cebmobileapi.azure-api.net/dotrez-prod/api/v1/Token'
        tracking_id = random.randint(100000, 999999)
        headers = {
            'Host': "cebmobileapi.azure-api.net",
            'loggly-tracking-id': "%d" % tracking_id,
            'Accept': "application/json",
            'Proxy-Connection': "keep-alive",
            'Accept-Language': "zh-cn",
            'Accept-Encoding': "gzip,deflate",
            'Content-Type': "application/json; charset=utf-8",
            # 'User-Agent': "Cebu%20Pacific/40467 CFNetwork/758.5.3 Darwin/15.6.0",
            'User-Agent': "Cebu%20Pacific/41137 CFNetwork/758.5.3 Darwin/15.6.0",
            'Connection': "keep-alive",
            'ocp-apim-subscription-key': spider.header_key,
            'Cache-Control': "no-cache"
        }
        res = requests.post(url, headers=headers)
        cookies_dict = res.cookies.get_dict()
        dotrez = cookies_dict['dotrez']
        cookies = [{u'domain': u'cebmobileapi.azure-api.net', u'secure': False, u'value': unicode(dotrez), u'expiry': None,
                 u'path': u'/', u'httpOnly': False, u'name': u'dotrez'}]
        res_dict = res.json()
        token_15m = res_dict['data']['token']
        spider.log("new token: %s" % token_15m, 20)
        return token_15m, cookies, tracking_id


class B5jProxyMiddleware:
    def __init__(self):
        self.proxy = None
        self.run_time = 0

    def process_request(self, request, spider):
        # 每隔10分钟设置代理为None
        now = time.time()
        if spider.banned is True:
            self.proxy = _get_proxy(spider)
        elif now - self.run_time > 60 * 10:
            self.proxy = None
            self.run_time = now

        request.meta['proxy'] = self.proxy


class TrProcessCookies(CookiesBase):
    def __init__(self):
        super(TrProcessCookies, self).__init__()
        self.firefox_options.add_argument('-headless')
        # 不加载图片
        self.firefox_profile.set_preference('permissions.default.image', 2)
        self.index_url = 'https://makeabooking.flyscoot.com'
        self.num = 1
        self.cookies = None

    def process_response(self, request, response, spider):
        if response.status != 200:
            spider.banned = True
            # return request
        # else:
        return response

    def process_request(self, request, spider):
        if 'redirect_urls' not in request.meta and 'origin' in request.meta:
            while True:
                self.proxy = _get_proxy(spider)
                # 初始化浏览器
                if not self.driver:
                    self.init_browser(spider)
                try:
                    # 模拟请求初始页
                    self.driver.get(request.url)
                    # 等待数据
                    _input = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="header-form-oneway"]')
                        ))
                except Exception as e:
                    # traceback.print_exc()
                    spider.log(e, 40)
                    spider.log('browser error, 8 seconds after the restart.', 40)
                    try:
                        self.driver.close()
                        self.driver = None
                    except:
                        self.driver = None

                    if not spider.proxy:
                        time.sleep(8)
                else:
                    break

            # 设置cookies
            self.cookies = self.driver.get_cookies()
            def x_update(x):
                x[u'expiry'] = None
                return x
            request.cookies = map(x_update, self.cookies)

            # 清除cookies
            spider.log('delete_all_cookies', 20)
            self.driver.delete_all_cookies()
            # 注释掉以后不再关闭浏览器
            if self.num % 10 == 0:
                spider.log('browser closed.', 20)
                self.driver.close()
                self.driver = None
            self.num += 1

        if spider.proxy and spider.banned is True:
            self.proxy = _get_proxy(spider)
        request.meta['proxy'] = self.proxy


class HvProcessCookies(CookiesBase):
    def __init__(self):
        super(HvProcessCookies, self).__init__()
        # self.firefox_options.add_argument('-headless')
        self.num = 1

        self.index_url = 'https://www.transavia.com/en-EU/book-a-flight/flights/search/'

    def process_response(self, request, response, spider):
        if response.status != 200 and response.status != 302:
            spider.log(response.status, 40)
        return response

    def process_request(self, request, spider):
        if 'origin' in request.meta:
            if spider.proxy:
                self.proxy = _get_proxy(spider)
            while True:
                # 初始化浏览器
                if not self.driver:
                    self.init_browser(spider)
                try:
                    # 模拟请求初始页
                    self.driver.get(self.index_url)

                    # 等待数据
                    _input = WebDriverWait(self.driver, 20).until(
                        EC.presence_of_element_located(
                            (By.XPATH, '//*[@id="flights"]/input')
                        ))
                except Exception as e:
                    spider.log(e, 40)
                    try:
                        self.driver.close()
                        self.driver = None
                    except:
                        self.driver = None
                    if not spider.proxy:
                        spider.log('browser error, 8 seconds after the restart.', 40)
                        time.sleep(8)
                else:
                    __RequestVerificationToken = _input.get_attribute('value')
                    break

            # 设置cookies
            cookies = self.driver.get_cookies()

            # 清除cookies
            spider.log('delete_all_cookies', 20)
            self.driver.delete_all_cookies()
            # # 注释掉以后不再关闭浏览器
            # if self.num % 10 == 0:
            #     spider.log('browser closed.', 20)
            #     self.driver.close()
            #     self.driver = None
            # self.num += 1

            try:
                body = json.loads(request.body)
                body.update({'__RequestVerificationToken': __RequestVerificationToken})
                request._set_body(parse.urlencode(body))

                request.cookies = cookies
            except Exception as e:
                spider.log(e, 40)
                # traceback.print_exc()

        request.meta['proxy'] = self.proxy


class AsProcessProxy(object):
    def __init__(self):
        self.proxy = None
        self.run_time = 0

    def process_response(self, request, response, spider):
        if response.status == 403:
            spider.log('%s Change Proxy \nSleep...' % response.status, 40)
            spider.banned = True
            return request
        return response

    def process_request(self, request, spider):
        # 每隔10分钟设置代理为None
        now = time.time()
        if spider.banned is True:
            # 有代理换代理,没代理休息2分钟
            if spider.proxy:
                self.proxy = _get_proxy(spider)
            else:
                spider.log('be banned, sleep 2m...', 20)
                time.sleep(60*2)
        elif now - self.run_time > 60 * 10:
            self.proxy = None
            self.run_time = now

        request.meta['proxy'] = self.proxy
