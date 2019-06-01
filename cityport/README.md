# 本项目用于对航司航线的的处理

项目环境： python3

## 项目目录
```
all_route/
    VY.csv
    ...
carrier/
    tw.py
    ...
updated_ports/
    VY.csv
    ...
handle_xlsx.py
index.py
```
- all_route中的csv文件是该航司存在的所有航线
- carrier中存的py文件是生成该航司航线的脚本代码
- updated_ports中的csv文件是从线上数据库中获取的有航班的航线。

再有新航司生成， 请自行上传对应的csv到all_route和对应脚本到carrier。

# city or port???

## city:
   - VY
   - LY

其余全是机场


