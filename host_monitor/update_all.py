# encoding:utf-8
from monitor import monitor
import sys, settings, time, re
class update_hosts(monitor):

    def gen_update_hosts(self, spiders):
        datas = []
        hosts = set()
        end = re.compile(r'-proxy$')

        for spider in spiders:
            host, carrier, number = spider.split(':')
            device = end.sub('', host)
            if host.endswith('-test'):
                continue
            device = device.replace('-high', '')
            device = device.replace('-chrome', '')
            device = device.replace('-firefox', '')
            hosts.add(device)

        downloads_cmd = '~/spider/update_and_restart_all/download.sh'
        # downloads_cmd = '~/spider/update_and_restart_all/restart.sh'
        datas.insert(0, {'cmd': downloads_cmd, 'devices': list(hosts)})
        print(datas)
        self.post_cmd(datas)




if __name__ == '__main__' :
    mon = update_hosts()
    content = mon.get_content()
    all_spiders = mon.get_all_spider(content)
    mon.gen_update_hosts(all_spiders)