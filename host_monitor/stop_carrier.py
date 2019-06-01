# encoding:utf-8
from monitor import monitor
import sys, settings, time, re
class kill_monitor(monitor):

    def gen_kill_cmd(self, spiders):
        """
        完全地杀死某个爬虫，不再启动
        :param spiders: get states里获取到的爬虫名字字符串列表
        :return:
        """
        datas = []
        hosts = set()
        end = re.compile(r'-proxy$')
        for spider in spiders:
            host, carrier, number = spider.split(':')
            device = end.sub('', host)
            key = '%s -a host_name=%s -a num=%s' % (carrier.lower(), host, number)
            if device not in hosts:
                cmd_kill = "ps -ef | grep '%s_man.py' | grep -v grep | cut -c 9-15 | xargs kill -9" % carrier.lower()
                hosts.add(device)
                data_kill = {'cmd': cmd_kill, 'devices': [device]}
                datas.append(data_kill)
            cmd = "ps -ef | grep '%s' | grep -v grep | cut -c 9-15 | xargs kill -9" % key
            data = {'cmd': cmd, 'devices': [device]}
            datas.append(data)
        downloads_cmd = '~/spider/update_and_restart_all/download.sh'
        # downloads_cmd = '~/spider/update_and_restart_all/restart.sh'
        datas.insert(0, {'cmd': downloads_cmd, 'devices': list(hosts)})
        print(datas)
        self.post_cmd(datas)




if __name__ == '__main__' :
    mon = kill_monitor()
    carrier = sys.argv[1].upper() or False
    if carrier:
        content = mon.get_content()
        all_spiders = mon.get_all_spider(content)
        spiders = mon.get_spider_by_name(all_spiders, carrier)
        mon.gen_kill_cmd(spiders)