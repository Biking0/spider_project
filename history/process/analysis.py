import sys
import logging

import gevent


import settings
from utils import util
from utils.mysql import MySql
from process.data import Handle


class Start:

    hand = Handle()

    db = MySql()

    def __init__(self, *args, **kwargs):
        self.carrier = kwargs.get('carrier', settings.CARRIER)
        self.ts = kwargs.get('ts', util.yesterday())

    def data_from_request(self, carrier=None, ts=None):
        if not carrier:
            carrier = self.carrier
        if not ts:
            ts = self.ts
        for base in util.get_id(carrier, ts):
            id = base.get('id')
            print(id)
            series = util.get_history('', id)
            print(series)
            self.hand.volcano(series)

    def data_from_db(self, carrier=None, ts=None):
        if not carrier:
            carrier = self.carrier
        if not ts:
            ts = self.ts
        # ids = self.db.get_id(carrier, ts)
        for id in self.db.get_id(carrier, ts):
            series = self.db.get_series(id, ts)
            if len(series) <= 1:
                continue
            self.hand.volcano_by_pro(series)


if __name__ == '__main__':
    st = Start()
    # st.data_from_request('ZE', '20190212')
    # st.data_from_db('TW', '20190217')


