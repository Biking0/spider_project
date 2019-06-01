# -*- coding: utf-8 -*-
import scrapy,re,time,json,datetime,logging
from wow_spider.items import WowSpiderItem
from utils import dataUtil
from utils import pubUtil



class MmSpider(scrapy.Spider):
    name = 'mm'
    allowed_domains = ['flypeach.com']
    start_urls = ['https://mbook.flypeach.com/sp/index.php?langculture=ja-jp']
    carrier = 'MM'
    version = 1.8
    task = []
    isOK = False
    isCOOKIE = True
    custom_settings = dict(
        DOWNLOADER_MIDDLEWARES={
            # 'lamudatech_dev.middlewares.LamudatechDevDownloaderMiddleware': 543,
            'wow_spider.middlewares.StatisticsItem': 400,
            'wow_spider.middlewares.MMProxyMiddleware': 200,
            'wow_spider.middlewares.MMcookieMiddleware': 300,

        },
        DOWNLOAD_TIMEOUT=30,
        # LOG_LEVEL = 'DEBUG',
        PROXY_TRY_NUM=8,
        COOKIES_ENABLED=False,
        INVALID_TIME=45,
        CONCURRENT_REQUESTS=12,
        RETRY_ENABLED=False,

        # ITEM_PIPELINES = {
        #     'wow_spider.pipelines.LmdSpidersPipelineTest': 300,
        # },
        headers={
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Cache-Control': 'max-age=0',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Cookie': '__z_a=3089064027227988404322798;',#暂时定这个，防止验证码
            # 'Cookie':'multi_window_check_guid=5ABC69C7-2F03-35F8-0B2F-C6929D35A106; F_departure_cd=HKG; F_destination_cd=KIX; PEACHSESSID=1ebgnplhqni82sjggqj5lr2334; _td=94ccddf8-d7f3-402d-aa35-cd34a2f96d86; _ga=GA1.2.1305212214.1534319319; _gid=GA1.2.1040165706.1534319319; _gat=1; __ZEHIC5046=1534319311; _rt.uid=a1ce0190-a05f-11e8-f506-06ec66003718; _rt.xd=c7d62f4c; __z_a=591608728212513408212513',
            # 'Host': 'mbook.flypeach.com',
            'Origin': 'https://mbook.flypeach.com',
            'Referer': 'https://mbook.flypeach.com/sp/index.php?langculture=zh-cn',
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.84 Mobile Safari/537.36',
        },
        IP_URL='http://lumtest.com/myip.json',
        IP_PROXY='http://lum-customer-lamudatech-zone-zhuzhai-session-%s-country-hk:zh1a90pgpnmx@zproxy.lum-superproxy.io:22225',
        # IP_PROXY='http://lum-customer-henanzhenxiang-zone-zhuzhai-session-%s-country-hk:7zgxeegnwaeo@zproxy.lum-superproxy.io:22225',
        COOKIE_URL="https://mbook.flypeach.com/__zenedge/f",
        COOKIE_PAYLOAD = {
            "UserAgent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36",
            "Language": "zh-CN",
            "ColorDepth": 24,
            "PixelRatio": 1,
            "HardwareConcurrency": -1,
            "ScreenResolution": "1920x109",
            "AvailableScreenResolution": "1920x109",
            "TimezoneOffset": -480,
            "SessionStorage": True,
            "LocalStorage": True,
            "IndexedDb": True,
            "DocumentBody": False,
            "OpenDatabase": True,
            "CpuClass": "unknown",
            "Platform": "MacIntel",
            "DoNotTrack": "unknown",
            "IsAdBlock": True,
            "LiedLanguages": False,
            "LiedResolution": False,
            "LiedOs": False,
            "LiedBrowser": False,
            "PluginsString": "Chrome PDF Plugin::Portable Document Format::application/x-google-chrome-pdf:pdf;Chrome PDF Viewer::::application/pdf:pdf;Native Client::::application/x-nacl:,application/x-pnacl:",
            "Fonts": "notselected",
            "CanvasFingerprint": "yes,63aa818444e62bba77a7e3d4b97055fcc926f36d",
            "WebGl": "webgl fingerprint:0902675f2196d7d89ea7751211da3a7db20e7401;webgl extensions:ANGLE_instanced_arrays;EXT_blend_minmax;EXT_color_buffer_half_float;EXT_frag_depth;EXT_shader_texture_lod;EXT_texture_filter_anisotropic;WEBKIT_EXT_texture_filter_anisotropic;EXT_sRGB;OES_element_index_uint;OES_standard_derivatives;OES_texture_float;OES_texture_float_linear;OES_texture_half_float;OES_texture_half_float_linear;OES_vertex_array_object;WEBGL_color_buffer_float;WEBGL_compressed_texture_s3tc;WEBKIT_WEBGL_compressed_texture_s3tc;WEBGL_compressed_texture_s3tc_srgb;WEBGL_debug_renderer_info;WEBGL_debug_shaders;WEBGL_depth_texture;WEBKIT_WEBGL_depth_texture;WEBGL_draw_buffers;WEBGL_lose_context;WEBKIT_WEBGL_lose_context;webgl status:[1, 1],[1, 255.875],8,yes,8,24,8,16,80,16384,1024,16384,16,16384,15,16,16,1024,[16384, 16384],8,WebKit WebGL,WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium),0,WebKit,WebGL 1.0 (OpenGL ES 2.0 Chromium),Intel Inc.,Intel Iris OpenGL Engine,23,127,127,23,127,127,23,127,127,23,127,127,23,127,127,23,127,127,0,31,30,0,31,30,0,31,30,0,31,30,0,31,30,0,31,30",
            "TouchSupport": "0,false,false",
            "AudioContext": "ac-baseLatency:0.005804988662131519, ac-sampleRate:44100, ac-state:running, ac-maxChannelCount:2, ac-numberOfInputs:1, ac-numberOfOutputs:0, ac-channelCount:2, ac-channelCountMode:explicit, ac-channelInterpretation:speakers, an-fftSize:2048, an-frequencyBinCount:1024, an-minDecibels:-100, an-maxDecibels:-30, an-smoothingTimeConstant:0.8, an-numberOfInputs:1, an-numberOfOutputs:1, an-channelCount:1, an-channelCountMode:max, an-channelInterpretation:speakers, ",
            "Oscillator": "1cc83a4c2402fb648a460025a9501ee7f1d38813",
            "DynamicCompressor": "24.84720432711765,c7a775894a88da43902747cdd1d89278a13bac73",
            "HybridOscillator": "5524e5fdfc866dadf956ac89b2ca94bc7cf8fa18"
        },
        COOKIE_HEADERS = {
            'origin': "https://mbook.flypeach.com",
            'x-devtools-emulate-network-conditions-client-id': "553D99C2ECB35FA27C85A7876D9E874B",
            'user-agent': "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Mobile Safari/537.36",
            'content-type': "application/json",
            'accept': "*/*",
            'referer': "https://mbook.flypeach.com/sp/index.php?langculture=zh-cn",
            'accept-encoding': "gzip, deflate, br",
            'accept-language': "zh-CN,zh;q=0.9",
            'cache-control': "no-cache",
        },
        CURRENCY_CACHE={
            u'₩': u'KRW',  # 韩元
            u'￥': u'JPY',  # 日元
            u'THB': u'THB',
            u'HK$': u'HKD',  # 港币
            u'NT$': u'TWD',  # 台币
            u'CNY': u'CNY',
        },

    )

    def __init__(self, *args, **kwargs):
        cls = self.__class__
        super(cls, self).__init__(*args, **kwargs)
        self.portCitys = dataUtil.get_port_city()


    def start_requests(self):
        permins = 0
        print(pubUtil.heartbeat(self.host_name,self.name,self.num,permins,self.version))
        while True:
            #增加睡眠时间
            if pubUtil.get_mm_adult():
                result = pubUtil.getUrl('MM', 5)
                if not result:
                    logging.info('get task error')
                    time.sleep(10)
                    continue
                for data in result:
                    (dt, dep, arr) = pubUtil.analysisData(data)
                    # dep,arr,dt = 'KIX','HKG','2018-10-12'
                    # print(dep,arr,dt)
                    from_data = {
                        'F_departure_cd': dep,  # 出发
                        'F_destination_cd': arr,  # 到达
                        'F_go_ym': int(re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\1\2', dt)),
                        'F_go_d': int(re.sub(r'(\d{4})-(\d{2})-(\d{2})', r'\3', dt)),
                        'F_trip_type': 1,
                        'F_adult_count': 5,  # 座位
                        'F_child_count': 0,
                        'F_infant_count': 0,
                        'F_p_token': '',
                        'PCMD': 'searchflightresult',
                        'BPCMD': 'searchflight',
                        'Campaign': '',
                        'next': 'next',
                    }
                    # print(from_data)
                    form =''
                    for b in from_data:
                        form = form + b + '=' + str(from_data.get(b)) + '&'
                    invalid = {
                        'date': dt.replace('-', ''),
                        'depAirport': dep,
                        'arrAirport': arr,
                        'mins': self.custom_settings.get('INVALID_TIME'),
                    }
                    meta_data = dict(
                        invalid=invalid,
                        maxSeats=from_data.get('F_adult_count'),
                        year=dt[:4],
                        form=form
                    )


                    yield scrapy.Request(self.start_urls[0],
                                         method='POST',
                                         headers=self.custom_settings.get('headers'),
                                         body=form,
                                         callback=self.parse,
                                         meta={'meta_data':meta_data},
                                         errback=self.errback)
            else:
                print('Non-issue time,sleep:60s')
                time.sleep(60)




    def parse(self, response):
        self.isCOOKIE = True
        self.isOK = True
        # print('----------------------------')
        # print(response.text)
        #把当天的航班信息和价格信息分类
        time_numbers = response.xpath('//td[contains(@class,"fl_date")]')
        prices = response.xpath('//td[contains(@class,"outward-total-fare-td")]')
        # print('-'*50)
        # print(response.text)
        # print('+' * 50)
        if not time_numbers:
            # print('!'*30)
            # print '%s' % (response.text.decode('utf-8').encode('gbk', 'ignore'))
            # self.log("no data",40)
            try:
                page = response.xpath('//h2/text()')[0].extract()
                # print(page)
                # print(response.status)
                # # print response.text
                # # proxy_invalid = response.xpath('//td[4]/text()')[0].extract()
                # # print proxy_invalid
                # if response.status == 404:
                #     self.isOK = False
                #     yield scrapy.Request(self.start_urls[0],
                #                          method='POST',
                #                          headers=self.custom_settings.get('headers'),
                #                          body=response.meta.get('meta_data').get('form'),
                #                          callback=self.parse,
                #                          meta={'meta_data': response.meta.get('meta_data')},
                #                          errback=self.errback)
                if page == 'Are you human?':
                    self.isCOOKIE = False
                    yield scrapy.Request(self.start_urls[0],
                                         method='POST',
                                         headers=self.custom_settings.get('headers'),
                                         body= response.meta.get('meta_data').get('form'),
                                         callback=self.parse,
                                         meta={'meta_data': response.meta.get('meta_data')},
                                         errback=self.errback)
                self.task.append(response.meta.get('meta_data').get('invalid'))
            except:
                self.log("no data", 10)
                self.task.append(response.meta.get('meta_data').get('invalid'))
            return

        #循环取出每个航班信息,year指的是航班的年份
        year = response.meta.get('meta_data').get('year')
        # print(len(time_numbers))

        for i in range(len(time_numbers)):
            #取出当次的航班信息,出发时间，到达时间，航班号
            time_number = time_numbers[i].xpath('./span/text()').extract()
            # 出发时间
            deptime = time.strptime(year + time_number[0], '%Y%m/%d\xa0%H:%M')
            depTime = time.mktime(deptime)
            # 到达时间
            arrtime = time.strptime(year + time_number[1], '%Y%m/%d\xa0%H:%M')
            arrTime = time.mktime(arrtime)
            # 航班号
            flightNumber = time_number[2]
            carrier = re.search('\D{2}',time_number[2]).group()


            #根据n定位当前航班价格，总价除以maxSeats为单人价格
            maxSeats = response.meta.get('meta_data').get('maxSeats')
            try:
                price = prices[i].xpath('./div[@id="outward_hp_' + str(i+1) + '_total_fare"]//span/text()').extract()
            except:
                #这种情况是ip有问题，得到数据是错误的
                self.log('Dangerous error data....', 40)
                self.isOK = False
            if price[3] == '0':
                price = prices[i].xpath('//div[@id="outward_hpp_' + str(i+1) + '_total_fare"]//span/text()').extract()
            if price[3] == '0':
                price = prices[i].xpath('//div[@id="outward_prime_' + str(i+1) + '_total_fare"]//span/text()').extract()
            if price[3] == '0':
                self.task.append(response.meta.get('meta_data').get('invalid'))
                continue
            # print(price)
            # 取价格




            netFare = int(re.search(r"\d.*", price[0]).group().replace(',', '')) / maxSeats
            adultTax = int(re.search(r"\d.*", price[1]).group().replace(',', '')) / maxSeats
            #增加价格打折的判断
            promo = response.xpath('//td[@id="outward_hp_' + str(i+1) + '_list"]/@class').extract()[0].split(' ')
            if promo[-1] == 'promo':
                adultPrice = int(re.search(r"\d.*", price[3]).group().replace(',', '')) / maxSeats / 0.7
                cabin = 'S'
            else:
                cabin = 'X'
                adultPrice = int(re.search(r"\d.*", price[3]).group().replace(',', '')) / maxSeats
            # 判断网页信息是否虚假
            if not price[2]:
                return
            currency = self.custom_settings.get('CURRENCY_CACHE').get(price[2])

            depAirport = response.meta.get('meta_data').get('invalid').get('depAirport')
            arrAirport = response.meta.get('meta_data').get('invalid').get('arrAirport')

            isChange = 1
            segments = dict(
                flightNumber=flightNumber,
                aircraftType='',
                number=1,
                departureTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(depTime)),
                destinationTime=time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(arrTime)),
                airline=carrier,
                dep=depAirport,
                dest=arrAirport,
                seats=int(maxSeats),
                duration=dataUtil.gen_duration(depTime, arrTime),
                depTerminal=''
            )
            getTime = time.time()

            item = WowSpiderItem()
            item['flightNumber'] = flightNumber
            item['depTime'] = depTime
            item['arrTime'] = arrTime
            item['fromCity'] = self.portCitys.get(depAirport, depAirport)
            item['toCity'] = self.portCitys.get(arrAirport, arrAirport)
            item['depAirport'] = depAirport
            item['arrAirport'] = arrAirport
            item['currency'] = currency
            item['adultPrice'] = adultPrice
            item['adultTax'] = adultTax
            item['netFare'] = netFare
            item['maxSeats'] = maxSeats
            item['cabin'] = cabin
            item['carrier'] = carrier
            item['isChange'] = isChange
            item['segments'] = '[]'
            item['getTime'] = getTime
            yield item
            # print(item)


    def errback(self, failure):
        self.log('error downloading....', 40)
        self.isOK = False
        # print('-'*40)
        print(failure.value)
        yield failure.request
