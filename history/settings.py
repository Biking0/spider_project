# encoding: utf-8
GET_ID = 'http://task.jiaoan100.com/buddha/search_ids_flights'

GET_HISTORY = 'http://dx.spider.jiaoan100.com/bigdata/letsgo'

VALIDATE_URL = "http://task.jiaoan100.com/buddha/validate"

CON_CURRENT_NUM = 32


KEY_MAP = dict(
    f='flightNumber',
    id='id',
    aa='arrAirport',
    dt='depTime',
    at='arrTime',
    da='depAirport',
    fc='fromCity',
    tc='toCity',
    cur='currency',
    c='carrier',
    ad='addtime'
)

CARRIER = [
    'FR', 'U2', 'BE', 'EW', 'WW', 'DP',  # 欧洲
    'NK', 'WN', '4O',  # 美洲
    'TW', '7C', 'BX', 'ZE',  # Korean
    'TT', 'TR', 'PC', 'XQ', 'W6', '5J',
    'F3',
    'AQ',  # China
    # 一个官网多个代码
    'VJ', 'VZ',
    'VK', 'VY',
    'GK', '3K', 'JQ',
    'DY', 'D8', 'DI',
]

DB_HOST = '127.0.0.1'
DB_USER = 'root'
# DB_HOST = '192.168.112.12'
# DB_USER = 'qiao'
DB_PWD = '20111129snowwind'
DB_NAME = 'history'
DB_PORT = 3306