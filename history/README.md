克隆本项目后
在ubuntu环境下需先安装一些东西

```bash
sudo apt install libmysqlclient-dev
sudo apt-get install python3 python-dev python3-dev \
     build-essential libssl-dev libffi-dev \
     libxml2-dev libxslt1-dev zlib1g-dev \
     python-pip

```
start

```bash
cd history
pip install -r requirements.txt
python app.py st[起始时间] en[终止时间]
# 起始时间和终止时间格式如20180101， 如若不加默认的启动的前一天
```