# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class LmdSpidersItem(scrapy.Item):
    flightNumber = scrapy.Field()
    depTime = scrapy.Field()
    arrTime = scrapy.Field()
    depAirport = scrapy.Field()
    arrAirport = scrapy.Field()
    currency = scrapy.Field()
    adultPrice = scrapy.Field()
    adultTax = scrapy.Field()
    netFare = scrapy.Field()
    maxSeats = scrapy.Field()
    cabin = scrapy.Field()
    carrier = scrapy.Field()
    isChange = scrapy.Field()
    segments = scrapy.Field()
    getTime = scrapy.Field()
    fromCity = scrapy.Field()
    toCity = scrapy.Field()
    updateCount = scrapy.Field()
    info = scrapy.Field()  # 验价需要的信息
    stopCities = scrapy.Field()  # 经停中转站
    failCount = scrapy.Field()  # 国内国际线


