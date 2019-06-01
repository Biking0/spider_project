# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ExampleItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    flight_number = scrapy.Field()
    dep_time = scrapy.Field()
    arr_time = scrapy.Field()
    dep_port = scrapy.Field()
    arr_port = scrapy.Field()
    currency = scrapy.Field()
    adult_price = scrapy.Field()
    adult_tax = scrapy.Field()
    net_fare = scrapy.Field()
    max_seats = scrapy.Field()
    cabin = scrapy.Field()
    carrier = scrapy.Field()
    is_change = scrapy.Field()
    segments = scrapy.Field()
    get_time = scrapy.Field()
    from_city = scrapy.Field()
    to_city = scrapy.Field()
    info = scrapy.Field()
