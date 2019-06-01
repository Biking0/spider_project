import logging
from datetime import datetime, timedelta

import gevent

import settings
from utils import util
from utils.mysql import MySql
from process.data import Handle
from process.volcano import Volcano


class Run:

    db = MySql()
    hand = Handle()
    max_num = settings.CON_CURRENT_NUM
    g_pool = []
    carrier_map = dict(
        ZE={
            'days': 30,
            'filters': [Volcano]
        },
        TW={
            'days':30,
            'filters': [Volcano]
        }
    )
    yesterday = util.yesterday()

    def run_item(self, item, ts):
        item = self.hand.run_base(item)
        flight = item.get('flightNumber')
        id = item.get('id')
        logging.info('go on id: ' + str(id))
        series = util.get_history(flight, id)
        if series:
            ret = self.hand.run_active(series)
            item.update(ret)
        else:
            series = []
        if int(ts) <= int(self.yesterday):  # 如果是昨天及以前的数据， 则入库储存
            self.db.add_li(item, 'base_ticket', ['id'])
            self.db.add_li(series, 'history_' + ts, ['flightNumber', 'addtime'])

    def run_all(self, ts):
        carrier_all = settings.CARRIER
        self.db.create_table('history_' + ts)
        for carrier in carrier_all:
            logging.info('%s in %s is begin:' % (carrier, ts))
            for item in util.get_id(carrier, ts):
                self.g_pool.append(gevent.spawn(self.run_item, item, ts))
                if len(self.g_pool) > self.max_num:
                    gevent.joinall(self.g_pool)
                    self.g_pool.clear()

    def ana_all(self, ts=None, carriers=None):
        """
        分析全部数据
        :param ts:
        :param carriers:
        :return:
        """
        carriers = carriers or settings.CARRIER
        if ts:
            ts_date = datetime.strptime(ts, '%Y%m%d')
        else:
            ts_date = datetime.now() + timedelta(days=1)
        for carrier in carriers:
            data_map = self.carrier_map.get(carrier)
            if not data_map:
                continue
            logging.info('start analysis carrier : ' + carrier)
            days = data_map.get('days')
            filters = data_map.get('filters')
            mans = []
            for filter in filters:
                mans.append(filter(carrier))
            for day in range(days):
                this_date = (ts_date + timedelta(days=day)).strftime('%Y%m%d')
                for item in util.get_id(carrier, this_date, tp=4):
                    # self.ana_item(item, filters)
                    self.g_pool.append(gevent.spawn(self.ana_item, item, mans))
                    if len(self.g_pool) > self.max_num:
                        gevent.joinall(self.g_pool)
                        self.g_pool.clear()
                for man in mans:
                    man.record()

    def ana_item(self, item, mans):
        flight = item.get('flightNumber')
        id = item.get('id')
        logging.info('go on id: %s and fn: %s ' % (str(id), flight))
        series = util.get_history(flight, id)
        for man in mans:
            man.run(series)

