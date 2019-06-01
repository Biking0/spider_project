# encoding:utf-8
import requests, json, time, re, sys
import logging, traceback, settings, util
is_python3 = sys.version_info[0] == 3
if not is_python3:
    from sets import Set as set

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)

class monitor:

    def __init__(self):
        self.host_name = {}


    def get_content(self):
        try:
            res = requests.get(settings.SPIDER_STATUS, timeout=20)
            content_dict = json.loads(res.text)
            return content_dict
        except:
            time.sleep(10)
            logging.info('get_content error... ')
            return self.get_content()

    def get_spider_by_time(self, content):
        datas = content.get('data')
        invalid_spiders = []
        host_cond = {}
        for full_name in datas.keys():
            active = datas.get(full_name).split(',')[0]
            host_name = full_name.split(':')[0]
            if host_name.endswith('-high'): # 排除掉高优先级的爬虫
                print(host_name)
                continue
            if time.time() - int(active) <= settings.STANDARD:
                host_cond[host_name] = True
            else:
                invalid_spiders.append(full_name)
                host_cond.setdefault(host_name, False)
        invalid_hosts = [k for k in host_cond if not host_cond.get(k) and not k.endswith('-proxy')]
        return (invalid_spiders, invalid_hosts)

    def get_all_spider(self, content):
        datas = content.get('data')
        return datas.keys()

    def get_spider_by_name(self, spiders, name):
        final_spiders = []
        for spider in spiders:
            host, carrier, num = spider.split(':')
            if carrier == name:
                final_spiders.append(spider)
        return final_spiders

    def gen_restart_cmd(self, spiders):
        datas = []
        hosts = set()
        end = re.compile(r'-proxy$')

        for spider in spiders:
            host, carrier, number = spider.split(':')
            device = end.sub('', host)
            #hosts.add(device)
            key = '%s -a host_name=%s -a num=%s' % (carrier.lower(), host, number)
            cmd = "ps -ef | grep '%s' | grep -v grep | cut -c 9-15 | xargs kill -9" % key
            for end_str in settings.FILTER:
                device = device.replace(end_str, '')
            hosts.add(device)
            data = {'cmd': cmd, 'devices': [device]}
            datas.append(data)

        downloads_cmd = '~/spider/update_and_restart_all/download.sh'
        # downloads_cmd = '~/spider/update_and_restart_all/restart.sh'
        datas.insert(0, {'cmd': downloads_cmd, 'devices': list(hosts)})
        print(datas)
        self.post_cmd(datas)

    def gen_restart_hosts(self, spiders):
        datas = []
        hosts = set()
        end = re.compile(r'-proxy$')

        for spider in spiders:
            host, carrier, number = spider.split(':')
            device = end.sub('', host)
            hosts.add(device)

        # downloads_cmd = '~/spider/update_and_restart_all/download.sh'
        downloads_cmd = '~/spider/update_and_restart_all/restart.sh'
        datas.insert(0, {'cmd': downloads_cmd, 'devices': list(hosts)})
        print(datas)
        self.post_cmd(datas)

    def format_data(self, content):
        body = '<ul>'
        for k, v  in content.items():
            body += '<li>%s: %s</li>' % (k, v)
        body += '</ul>'

        return body

    def gen_cmd(self, spiders): # 例行检查，对挂掉的爬虫发送kill命令
        datas = []
        end = re.compile(r'-proxy$')
        for spider in spiders:
            host, carrier, number = spider.split(':')
            if host.endswith('-high'):
                print(host)
                continue
            if carrier not in settings.DONT_ALLOWED:
                device = end.sub('', host)
                key = '%s -a host_name=%s -a num=%s' % (carrier.lower(), host, number)
                cmd = "ps -ef | grep '%s' | grep -v grep | cut -c 9-15 | xargs kill -9" % key
                data = {'cmd':cmd, 'devices': [device]}
                datas.append(data)
        if not len(datas):
            return
        self.post_cmd(datas)

    def post_cmd(self, datas): # push 命令方法
        try:
            # print(json.dumps(datas))
            res = None
            for i in range(0, len(datas), 20):
                print('ok')
                j = len(datas) if i + 20 > len(datas) else i + 20
                res = requests.post(settings.CMD_URL, data=json.dumps(datas[i: j]), timeout=settings.DOWNLOAD_TIMEOUT)
            print(res.text)
            status = json.loads(res.text).get('status')
            if status:
                logging.info(str(datas))
                print(len(datas))
        except:
            traceback.print_exc()

    def check_hosts(self):
        try:
            this_time = time.time()
            res = requests.get(settings.HOST_STATUS, timeout=settings.DOWNLOAD_TIMEOUT)
            data = json.loads(res.text)
        except:
            traceback.print_exc()
            return
        stamp_dict = data.get('stamp')
        str_dict = data.get('str')
        for k, v in stamp_dict.items():
            if this_time - float(v) > settings.STANDARD:
                self.host_name[k.split(':')[1]] = str_dict.get(k)
        if not len(self.host_name):
            return
        body = self.format_data(self.host_name)
        self.host_name = {}

        util.send_email('Notice! invalid_hosts', body, settings.HOST_RECEIVERS)
        # util.send_email('Notice! invalid_hosts', body, settings.HOST_RECEIVERS_TEST)


    def check(self):
        data = self.get_content()
        (spiders, hosts) = self.get_spider_by_time(data)
        if not len(spiders):
            time.sleep(settings.DURATION)
        self.gen_cmd(spiders)
        self.check_hosts()



if __name__ == '__main__':
    mon = monitor()
    while True:
        mon.check()
        time.sleep(settings.DURATION)
