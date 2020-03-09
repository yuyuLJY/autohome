# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CarmodelItem(scrapy.Item):
    brand = scrapy.Field()
    car_company = scrapy.Field()
    car_model_id = scrapy.Field()
    car_model = scrapy.Field()
    car_model_url = scrapy.Field()


class CartypeItem(scrapy.Item):
    car_model_id = scrapy.Field()
    car_type = scrapy.Field()


class CararticleItem(scrapy.Item):
    car_model_id = scrapy.Field()
    article_url = scrapy.Field()
    article_title = scrapy.Field()
    article_date = scrapy.Field()
    auther = scrapy.Field()
    view_times = scrapy.Field()
    reply_times = scrapy.Field()
    article_category = scrapy.Field()
    editor_tags = scrapy.Field()


class CardetailItem(scrapy.Item):
    car_price_high = scrapy.Field()
    car_price_low = scrapy.Field()
    car_rival_1 = scrapy.Field()
    car_rival_2 = scrapy.Field()
    car_rival_3 = scrapy.Field()
    car_rival_4 = scrapy.Field()
    car_rival_5 = scrapy.Field()
    car_model_id = scrapy.Field()


class WomItem(scrapy.Item):
    #
    car_model_id = scrapy.Field()
    user_id = scrapy.Field()
    buy_address = scrapy.Field()
    buy_date = scrapy.Field()
    buy_price = scrapy.Field()
    car_gas = scrapy.Field()
    car_distance = scrapy.Field()
    evl_space = scrapy.Field()
    evl_engine = scrapy.Field()
    evl_drive = scrapy.Field()
    evl_gas = scrapy.Field()
    evl_comfort = scrapy.Field()
    evl_exterior = scrapy.Field()
    evl_interior = scrapy.Field()
    evl_price_perfomance = scrapy.Field()
    buy_purpose = scrapy.Field()
    car_wom_date = scrapy.Field()
    car_wom_month = scrapy.Field()
    car_model_detail = scrapy.Field()


class ArticleItem(scrapy.Item):
    article = scrapy.Field()
    filename = scrapy.Field()


class KoubeiItem(scrapy.Item):
    #
    seriesid = scrapy.Field()
    brandid = scrapy.Field()
    powertype = scrapy.Field()
    powername = scrapy.Field()
    isbattery = scrapy.Field()
    userId = scrapy.Field()
    userName = scrapy.Field()
    specid = scrapy.Field()
    specname = scrapy.Field()
    boughtcityname = scrapy.Field()
    boughtdate = scrapy.Field()
    boughtPrice = scrapy.Field()
    actualOilConsumption = scrapy.Field()
    actualBatteryConsumption = scrapy.Field()
    drivekilometer = scrapy.Field()
    spaceScene_score = scrapy.Field()
    powerScene_score = scrapy.Field()
    maneuverabilityScene_score = scrapy.Field()
    oilScene_score = scrapy.Field()
    batteryScene_score = scrapy.Field()
    comfortablenessScene_score = scrapy.Field()
    apperanceScene_score = scrapy.Field()
    internalScene_score = scrapy.Field()
    costefficientScene_score = scrapy.Field()
    purpose = scrapy.Field()
    eid = scrapy.Field()
    created = scrapy.Field()


class DealerItem(scrapy.Item):
    dealeraddress = scrapy.Field()
    dealerid = scrapy.Field()
    dealername = scrapy.Field()
    dealertags = scrapy.Field()
    dealertype = scrapy.Field()
    typename = scrapy.Field()
    provinceid = scrapy.Field()
    cityid = scrapy.Field()
    cityname = scrapy.Field()
    sale_area = scrapy.Field()


class quoteItem(scrapy.Item):
    dealerid = scrapy.Field()
    seriesid = scrapy.Field()
    specid = scrapy.Field()
    specname = scrapy.Field()
    price = scrapy.Field()
    priceoff = scrapy.Field()
    maxprice = scrapy.Field()
    maxOriginalPrice = scrapy.Field()
    minOriginalPrice = scrapy.Field()


class ConfigItem(scrapy.Item):
    car_model_id = scrapy.Field()
    specid = scrapy.Field()
    config_data = scrapy.Field()
    specname = scrapy.Field()
    guidePrice = scrapy.Field()
    ttm = scrapy.Field()
    length = scrapy.Field()
    height = scrapy.Field()
    width = scrapy.Field()
    wheelbase = scrapy.Field()


class NewbrandItem(scrapy.Item):
    car_model_id = scrapy.Field()
    month = scrapy.Field()


class CarbasicInfo(scrapy.Item):
    # 汽车类别基本信息
    # e.g. "奥迪","中大型车","德国","一汽-大众奥迪","奥迪A6L","40.98-65.08万","18"
    company_bigtype = scrapy.Field()  # "奥迪"
    type_name = scrapy.Field()  # "中大型车"
    nation_name = scrapy.Field()  # "德国"
    car_company = scrapy.Field()  # "一汽-大众奥迪"
    car_brand = scrapy.Field()  # "奥迪A6L"
    price = scrapy.Field()  # "40.98-65.08万"
    car_brand_id = scrapy.Field()  # "18"
