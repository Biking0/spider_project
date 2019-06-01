# 配置环境
## 安装python3及对应的pip
```
sudo apt-get install python3
sudo apt-get install python3-pip
```
## 安装virtualenv
```
pip3 install virtualenv
```
## 创建虚拟环境
```
virtualenv py3
```
如果显示的是python2的虚拟环境
```
rm -rf py3
virtualenv -p /usr/bin/python3.* py3[环境名]
```
## 启动虚拟环境
```
source py3/bin/activate
```
## 安装包
```
pip install -r requirements.txt
```
# 运行
```
python proxy_daxiang.py
python proxy_xun.py
```