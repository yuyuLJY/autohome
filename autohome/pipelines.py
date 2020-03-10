# -*- coding: utf-8 -*-
import pymongo
import pymysql
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html



class AutohomePipeline(object):
    def __init__(self):

        pass
        # self.connection = pymysql.connect(user='root', password='ycs9801', host='127.0.0.1', port=3306,
        #                              db='autohome_db', charset='utf8mb4')

    def process_item(self, item, spider):

        if spider.name == 'koubei':
            keys = item.keys()
            #sql = 'insert into car_wom(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,' \
            #      '%s, %s, %s, %s, %s, %s, %s)' % tuple(keys)

            #sql = sql + ' values ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s",' \
            #            '"%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s","%s", "%s", "%s")' % tuple([item[key] for key in keys])
            print(item["eid"])
            #self.cursor.execute(sql)
            #self.connection.commit()


        return item

class CarBasicInfoPipeline(object):
    #汽车类别信息的Pipeline
    def __init__(self):
        # 必须写上charset='utf8'，不然可能有编码错误
        self.db = pymysql.connect(host='localhost', user='root', port=3306, charset='utf8')
        self.cursor = self.db.cursor()
        self.cursor.execute('use spiders')
        sql = 'CREATE TABLE IF NOT EXISTS carBasicInfo(' \
              'company_bigtype VARCHAR(255) NOT NULL,' \
              'type_name VARCHAR(255) NOT NULL,' \
              'nation_name VARCHAR(255) NOT NULL,' \
              'car_company VARCHAR(255) NOT NULL,' \
              'car_brand VARCHAR(255) NOT NULL,' \
              'price VARCHAR(255),' \
              'car_brand_id INT NOT NULL PRIMARY KEY)'
        self.cursor.execute(sql)

    def process_item(self, item, spider):
        data = {
            'company_bigtype':item['company_bigtype'],
            'type_name' :item[ 'type_name'],
            'nation_name': item['nation_name'],
            'car_company' :item['car_company'],
            'car_brand' :item['car_brand'],
            'price':item['price'],
            'car_brand_id':item['car_brand_id']
        }
        table = 'carBasicInfo'
        keys = ','.join(data.keys())
        values = ','.join(['%s']*len(data))
        sql = 'INSERT INTO {table}({keys}) VALUES({values})'.format(table=table,keys=keys,values=values)
        try:
            if self.cursor.execute(sql,tuple(data.values())):
                print('Suffessful')
                self.db.commit()
        except:
            print('Fail')
            self.db.rollback()
        return item

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        self.db.close()
