# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from lmd_spiders import settings
import requests, json, logging, random, time, traceback
from bs4 import BeautifulSoup
from jsonpath import jsonpath
from lmd_spiders.spiders.w6 import W6Spider


class BxProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0
        self.is_ok = True

    def process_response(self, request, response, spider):
        if response.text == 'null':
            self.is_ok = False
            spider.log('null ip: %s' % request.meta.get('proxy'), 20)
            return request
        self.is_ok = True
        return response

    def process_request(self, request, spider):
        if hasattr(spider, 'proxy') and spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)

    def _get_proxy(self, spider):
        num = spider.custom_settings.get('CONCURRENT_REQUESTS')
        if self.is_ok and spider.is_ok:
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

class A6eSessionMiddleware(object):

    def __init__(self):
        self.session = None

    def process_request(self, request, spider):
        if not self.session:
            self.session = self.get_session(spider)
        request.headers['authorization'] = self.session

    def get_session(self, spider):
        headers = spider.custom_settings.get('GET_SESSION_HEADERS')
        url = spider.custom_settings.get('GET_SESSION_URL')
        post_data = spider.custom_settings.get('GET_SESSION_DATA')
        while True:
            try:
                res = requests.post(url, data=json.dumps(post_data), headers=headers, timeout=settings.DOWNLOAD_TIMEOUT)
                data = json.loads(res.text)
                session = data.get('data').get('token').get('token')
                return session
            except Exception as e:
                spider.log('get session error: %s' % e, 40)
                time.sleep(5)

class SLWscMiddleware(object):

    def __init__(self):
        self.wsc = ''
        self.proxy = ''
        self.isOK = True
        self.proxyCount = 0
        self.backSelfCount = 0

    def process_response(self, request, response, spider):
        if response.status != 200:
            logging.info('response error,  Change ip')
            self.isOK = False
            return request
        self.isOK = True
        return response

    def process_request(self, request, spider):
        if not self.wsc:
            self.wsc = self.get_wsc(spider)
        request.headers['WscContext'] = self.wsc
        if spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)

    def get_wsc(self, spider):
        data = spider.custom_settings.get('GET_WSC_DATA')
        res = requests.post(spider.custom_settings.get('GET_WSC_URL'), data=json.dumps(data), headers=spider.custom_settings.get('DEFAULT_REQUEST_HEADERS'), timeout=settings.GET_URL_TIMEOUT)
        logging.info('get_wsc' + str(res.status_code))
        return res.headers.get('WscContext')

    def _get_proxy(self, spider):
        if spider.isOK and self.isOK:
            return self.proxy
        if self.proxyCount < 10:
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
            li = json.loads(requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=SL', timeout=settings.GET_URL_TIMEOUT).text)
            logging.info('Proxy Num: ' + str(len(li)))
            logging.info(str(li))
            self.proxy = random.choice(li).decode('ascii') or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''


class V7ProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0

    def process_response(self, request, response, spider):
        if response.status == 403:
            spider.log('403 error...')
            spider.isOK = False
            return request
        return response

    def process_request(self, request, spider):
        if hasattr(spider, 'proxy') and spider.proxy:
            proxy = self._get_proxy(spider)
            if proxy:
                request.meta['proxy'] = 'https://' + proxy

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
            # self.proxy = random.choice(li).decode('ascii') or ''
            self.proxy = random.choice(li) or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''


class ProxyMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.proxyCount = 0
        self.backSelfCount = 0

    def process_request(self, request, spider):
        if hasattr(spider, 'proxy') and spider.proxy:
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

class MmCookieMiddleware(object):
    def __init__(self):
        self.wsc = ''
        self.proxy = ''
        self.isOK = True
        self.proxyCount = 0
        self.backSelfCount = 0

    def process_response(self, request, response, spider):
        if response.status != 200:
            logging.info('response error,  Change ip')
            self.isOK = False
            return request
        self.isOK = True
        return response

    def process_request(self, request, spider):
        if spider.proxy:
            request.meta['proxy'] = self._get_proxy(spider)
        cookies = self.get_cookies(spider, request.meta.get('post_data'), self.proxy)
        if not cookies:
            return request
        else:
            request.cookies = cookies
     
    def get_cookies(self, spider, data, ip_port):
        """
            确保每个请求执行之前都有获取到它自己的唯一的cookies
        """
        url = spider.start_urls[0]
        headers = spider.custom_settings.get('DEFAULT_REQUEST_HEADERS')
        if ip_port:
            proxy = {
                'http': 'http://%s' % ip_port,
                'https': 'https://%s' % ip_port,
            }
        try:
            print(proxy)
            response = requests.post(url, data=data, proxies=proxy, headers=headers, timeout=5, allow_redirects=False)
            se_id = response.cookies.get('_session_id')
            if not se_id:
                self.isOK = False
                spider.log('not se_id', 30)
                return
            self.isOK = True
            reqid = response.cookies.get('reqid')
            print(reqid)
            return {'_session_id': se_id, 'reqid': reqid}
        except:
            self.isOK = False
            spider.log('get cookie error', 30)

    def _get_proxy(self, spider):
        num = spider.custom_settings.get('PROXY_TRY_NUM', 10)
        if self.isOK:
            return self.proxy
        if self.proxyCount < num:
            self.proxyCount = self.proxyCount + 1
            logging.info('using old proxy:' + self.proxy)
            return self.proxy

        self.proxyCount = 0
        if self.backSelfCount >= 10:
            #try 10 times and back to self ip
            logging.info('using self ip')
            self.backSelfCount = 0
            self.proxy = ''
            return self.proxy

        try:
            params = {'carrier': spider.name}
            li = json.loads(requests.get(settings.GET_PROXY_URL, params=params, timeout=settings.GET_URL_TIMEOUT).text)
            logging.info('Proxy Num: ' + str(len(li)))
            # logging.info(str(li))
            self.proxy = random.choice(li).decode('ascii') or ''
            self.backSelfCount = self.backSelfCount + 1
        except:
            # traceback.print_exc()
            logging.info('get proxy error....')
        finally:
            return self.proxy or ''

class W6CookieMiddleware(object):

    def __init__(self):
        self.proxy = ''
        self.sid, self.dt = self.get_sid(W6Spider)

    # def process_response(self, request, response, spider):
    #     if response.status == 404:
    #         logging.info('response error,  Change ip')
    #         return request

    def process_request(self, request, spider):
        if not spider.isOK:
            self._get_proxy(spider)
        if not self.sid:
            self.sid, self.dt = self.get_sid(spider)
        # print(request.headers)
        data = request.body
        data_dict = json.loads(data)
        data_dict['Process']['ClientSessionId'] = self.sid
        data_dict['Process']['ClientDate'] = self.dt
        request._set_body(json.dumps(data_dict))
        if spider.proxy:
            request.meta['proxy'] = self.proxy


    def get_sid(self, spider):
        dt = time.strftime('%Y-%m-%dT%H:%M:%S', time.localtime(time.time() - 60))
        data = spider.custom_settings.get('GET_SESSION_DATA')
        data['Process']['ClientDate'] = dt
        url = spider.custom_settings.get('GET_SESSION_URL')
        header = spider.custom_settings.get('DEFAULT_REQUEST_HEADERS')
        res = None

        try:
            if spider.proxy:
                proxy = {
                    'http': 'http://%s' % self.proxy,
                    'https': 'http://%s' % self.proxy,
                }
            else:
                proxy = ''
            print(proxy)
            res = requests.post(url, data=json.dumps(data), proxies=proxy, headers=header, verify=False, timeout=settings.DOWNLOAD_TIMEOUT)
            print('gotID')
        except:
            # traceback.print_exc()
            time.sleep(2)
            self._get_proxy(spider)
            return None, None

        data = json.loads(res.text)
        sessionid = jsonpath(data, '$..ClientSessionId')[0]
        return (sessionid, dt)

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


class TWCookieMiddleware(object):

    def __init__(self):
        self.searchId = None
        self.cookies = {"TWAYLANG": 'EN'}

    def process_response(self, response, request, spider):
        if response.status == 302:
            logging.info('302, change cookies')
            cookies, self.searchId = self._get_searchId(spider)
            self.cookies.update(cookies)
            return request
        return response

    def process_request(self, request, spider):
        if not self.searchId:
            cookies, self.searchId = self._get_searchId(spider)
            self.cookies.update(cookies)
        request._set_url(request.url + '&searchAvailId=%s' % self.searchId)
        request.cookies = self.cookies

    def _get_searchId(self, spider):
        headers = spider.custom_settings.get('COOKIE_HEADERS')
        url = spider.custom_settings.get('GET_COOKIES_URL')
        while True:
            try:
                res = requests.get(url, headers=headers, timeout=settings.GET_URL_TIMEOUT, verify=False)
                soup = BeautifulSoup(res.text, 'lxml')
                searchAvailId = soup.select_one('input[name="searchAvailId"]')['value']
                if searchAvailId:
                    logging.info(searchAvailId)
                    cookies = {'JSESSIONID': res.cookies.get('JSESSIONID')}
                    return (cookies, searchAvailId)
            except Exception as e:
                print(e)
                logging.info('get searchId and cookies error')
                time.sleep(5)

