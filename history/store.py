import sys
import logging

import gevent

import settings
from utils import util
from process.run import Run

logging.basicConfig(
    # filename='jq-spider-api.log', filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


def manage(st_ts, en_ts):
    run = Run()
    for date in util.get_dates(st_ts, en_ts):
        run.run_all(date)


if __name__ == '__main__':
    args = sys.argv
    l = len(args)
    st_ts = args[1] if l >= 2 else util.yesterday()
    en_ts = args[2] if l >= 3 else st_ts
    manage(st_ts, en_ts)
