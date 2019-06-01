#!/usr/bin/env bash
cd ~
. py3/bin/activate
cd history
git pull
pip install -r requirements.txt
nohup python store.py >/dev/null 2>&1 &