# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import MapCompose


def filter_string(value):
    if value :
        return value




class ElkoItem(scrapy.Item):

    title = scrapy.Field(input_processor=MapCompose(filter_string))
    price = scrapy.Field(input_processor=MapCompose(filter_string))
    code_elko = scrapy.Field(input_processor=MapCompose(filter_string))
    code_manufacture = scrapy.Field(input_processor=MapCompose(filter_string))
    na_sklade = scrapy.Field(input_processor=MapCompose(filter_string))
    manufacture = scrapy.Field(input_processor=MapCompose(filter_string))


class ProductItems(scrapy.Item):
    title = scrapy.Field(input_processor=MapCompose(unicode.strip, filter_string))
    key = scrapy.Field(input_processor=MapCompose(unicode.strip, filter_string))
    value = scrapy.Field(input_processor=MapCompose(unicode.strip, filter_string))
    case_type = scrapy.Field(input_processor=MapCompose(unicode.strip, filter_string))












