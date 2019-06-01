# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class FlightsItem(scrapy.Item):
    flightNumber = scrapy.Field() # 航班号
    depTime = scrapy.Field() # 出发时间
    arrTime = scrapy.Field() # 达到时间
    fromCity = scrapy.Field() # 出发城市
    toCity = scrapy.Field() # 到达城市
    depAirport = scrapy.Field() # 出发机场
    arrAirport = scrapy.Field() # 到达机场
    currency = scrapy.Field() # 货币种类
    adultPrice = scrapy.Field() # 成人票价
    adultTax = scrapy.Field() # 税价
    netFare = scrapy.Field() # 净票价
    maxSeats = scrapy.Field() # 可预定座位数
    cabin = scrapy.Field() # 舱位
    carrier = scrapy.Field() # 航空公司
    isChange = scrapy.Field() # 是否为中转 1.直达2.中转
    segments = scrapy.Field() # 中转时的各个航班信息
    addtime = scrapy.Field()
    getTime = scrapy.Field() # 获取信息时间
    updateCount = scrapy.Field() # 更新成功次数
    failCount = scrapy.Field() # 更新失败次数
