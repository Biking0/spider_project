from monitor import monitor
import sys, settings, time

if __name__ == '__main__' :
    mon = monitor()
    content = mon.get_content()
    all_spiders = mon.get_all_spider(content)
    mon.gen_restart_hosts(all_spiders)