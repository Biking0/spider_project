# 配置环境
## 安装virtualenv
```
pip install virtualenv
```
## 创建虚拟环境
如果python2与python3并存:
```
virtualenv -p /usr/bin/python2.7 py2[环境名]
```
没有python3:
```
virtualenv py2[环境名]
```
## 启动虚拟环境
```
source py2/bin/activate
```
## 安装包
```
pip install -r requirements.txt
```
如果scrapy安装失败，就再安装一下python-dev
```
sudo apt-get install python-dev
```
# 启动(lin-test上的第一个f3爬虫,数字不写的话默认为1)
```
python f3_man.py lin-test 1
```
