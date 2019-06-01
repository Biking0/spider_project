#!/usr/bin/env bash

source ~/projects/py3/bin/activate
pkill -9 python

cd ~/projects/proxy
git pull
pip install -r requirements.txt
#nohup python proxy_xun_day.py >/dev/null 2>&1 &

nohup python proxy_did.py >/dev/null 2>&1 &
# 运行十个proxy_daxiang
num=1
while(( $num <= 5 ))
do
    nohup python proxy_daxiang.py 2 >/dev/null 2>&1 &
    sleep 1
    let "num++"
done


# 更新运行monitor
cd ~/projects/host_monitor
git pull
nohup python monitor.py >/dev/null 2>&1 &

ps -xf | grep python
