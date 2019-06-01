# encoding=utf-8
# 7c
# by hyn
# 2018-12-17

city_data = [
    'ICN',
    'GMP',
    'PUS',
    'CJU',
    'TAE',
    'KWJ',
    'CJJ',
    'MWX',
    'USN',
]

# 笛卡尔积
for i in city_data:
    for j in city_data:
        if i != j:
            print i + ',' + j
