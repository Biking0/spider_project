from monitor import monitor
import sys, settings, time

if __name__ == '__main__' :
    mon = monitor()
    carrier = sys.argv[1].upper() or False
    if carrier:
        content = mon.get_content()
        all_spiders = mon.get_all_spider(content)
        spiders = mon.get_spider_by_name(all_spiders, carrier)
        mon.gen_restart_cmd(spiders)