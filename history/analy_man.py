import sys
import time
import logging

import settings
from process.run import Run

logging.basicConfig(
    # filename='jq-spider-api.log', filemode="w",
    level=logging.INFO,
    format="[%(asctime)s] %(name)s:%(levelname)s: %(message)s"
)


def manage(carrier):
    run = Run()
    while True:
        run.ana_all(carriers=carrier)
        time.sleep(10)


if __name__ == '__main__':
    args = sys.argv
    l_a = len(args)
    carrier = [args[1]] if l_a >= 2 else settings.CARRIER
    for i in args[2:]:
        carrier.append(i)
    manage(carrier)
