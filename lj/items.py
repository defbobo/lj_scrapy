# -*- coding: utf-8 -*-
import scrapy


class LjItem(scrapy.Item):
    url = scrapy.Field()
    location = scrapy.Field()
    area = scrapy.Field()
    layout = scrapy.Field()
    size = scrapy.Field()
    buildtime = scrapy.Field()
    price = scrapy.Field()

