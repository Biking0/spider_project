# encoding:utf-8
import sys
sys.path.append('..')
import time,logging
import hashlib, requests, traceback
import redis, random, json
import settings

class genProxy():

    proxy = None
    last_time = 0

    def genProxy(self):
        _version = sys.version_info

        is_python3 = (_version[0] == 3)

        orderno = "ZF20182110357G9Gk1C"
        secret = "450a760b60c94b0a85c6f315dd640219"

        ip = "forward.xdaili.cn"
        port = "80"

        ip_port = ip + ":" + port

        timestamp = str(int(time.time()))                # 计算时间戳
        string = ""
        string = "orderno=" + orderno + "," + "secret=" + secret + "," + "timestamp=" + timestamp

        if is_python3:
            string = string.encode()

        md5_string = hashlib.md5(string).hexdigest()                 # 计算sign
        sign = md5_string.upper()                              # 转换成大写

        auth = "sign=" + sign + "&" + "orderno=" + orderno + "&" + "timestamp=" + timestamp

        proxy = {"http": "http://" + ip_port, "https": "https://" + ip_port}
        headers = {"Proxy-Authorization": auth}
        #print(headers)
        #print(proxy)
        return (proxy, headers)

    def getHttpProxy(self, force_new=None):
        if not force_new and self.proxy:#time.time() - self.last_time <= 60 * 1.5:# 讯代理
            return self.proxy
        try: # 讯代理
            # db = redis.Redis('116.196.83.53', port=6379, db=1)
            # li = db.keys('proxy_key:Xproxy:*')
            content = requests.get('http://dx.proxy.jiaoan100.com/proxy/getproxy?carrier=tr')
            li = json.loads(content.text)
            logging.info('proxy Num: ' + str(len(li)))
            proxy = random.choice(li)
            if proxy:
                self.proxy = proxy
            else:
                self.proxy = ''
        except:
            traceback.print_exc()
        finally:
            return self.proxy



if __name__ == "__main__":
    g = genProxy()
    print(g.getHttpProxy())
