# -*-encoding:utf-8-*-
import scrapy
import json
import re
import math
import pandas as pd
from pathlib import Path
from items import KoubeiItem
from items import WomItem
#设置将python的默认编码，一般设置为utf8的编码格式
# 这是Python2的解决办法
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

class AppendSpider(scrapy.Spider):
    name = 'append_koubei'
    print('spider：',name)
    handle_httpstatus_list = [302 ,404 ,403 ,500 ,503]
    #口碑列表
    base_url = "https://koubei.app.autohome.com.cn/autov8.8.5/alibi/seriesalibiinfos-pm2-ss"
    #单条口碑
    wom_base_url = "https://koubei.app.autohome.com.cn/autov8.8.5/alibi/NewEvaluationInfo.ashx?eid="
    #单条口碑对应的评论
    reply_url="http://reply.autohome.com.cn/ShowReply/ReplyJsonredis.ashx?"  #count=5&page=2&id=1344220"
    reply_url_ext="&datatype=json&appid=5"
    dir = 'E:/autohome_data/' #TODO 更新后数据的存放位置
    id_list = [x[:-1] for x in open('data_car_id/car_id.txt' ,'r').readlines()]  # 打开文件，读取相应的行，并且用x[:-1]处理掉'/n'
    #start_urls = [base_url + car_model_id + '-st0-p1-s20-isstruct1-o0.json' for car_model_id in id_list]
    start_urls = []
    for car_model_id in id_list:
        base_url = "https://koubei.app.autohome.com.cn/autov8.8.5/alibi/seriesalibiinfos-pm2-ss"
        start_urls.append(base_url + car_model_id + '-st0-p1-s20-isstruct1-o0.json')

    # 把原来数据的更新时间读进去
    df = pd.read_csv('data_koubei/pre_day_comment.csv', sep=',', low_memory=False)
    day = df['day'].tolist()
    koubei_id = df['koubei_id'].tolist()
    koubei_id_dict = dict(zip(koubei_id, day))

    def parse(self, response):
        # 一页的口碑数据
        if response.status == 200:
            data = json.loads(response.body)
            result = data['result']
            pageindex = result['pageindex']  # 当前的口碑页数
            pagecount = result['pagecount']  # 总共的口碑页数
            seriesid = result['seriesid']
            wom_list = result['list'] # 口碑list
            for wom in wom_list:
                koubeiid = wom['Koubeiid']
                cur_post_time = wom['posttime']
                comment_num = wom['commentcount'] # 评论的个数
                #print('EID:',koubeiid,' 评论个数:',comment_num)

                # 判断这是否是一个新的EID
                if koubeiid in self.koubei_id_dict:
                    # 不是新EID，判断是否需要更新口碑
                    cur_post_day = self.get_day(cur_post_time)
                    pre_post_day = self.koubei_id_dict[koubeiid]
                    #print('更新时间', pre_post_day, cur_post_day)
                    if pre_post_day < cur_post_day:
                        wom_url = self.wom_base_url + str(koubeiid)
                        yield scrapy.Request(wom_url, self.wom_detail_parse)
                else:
                    # 这是新的EID,需要写进文件
                    #print('这是新的EID')
                    wom_url = self.wom_base_url + str(koubeiid)
                    yield scrapy.Request(wom_url, self.wom_detail_parse)

                # 如果有评论，把评论爬取出来
                if comment_num > 0:
                    myreply_url = 'https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId=' + \
                                  str(koubeiid) + '&pagesize=20&lastid=0&hot=0'
                    yield scrapy.Request(myreply_url, self.reply_parse)

            filename = response.url.split('/')[-1]
            self.save_data(filename,response.body)

            if pageindex < pagecount:
                url_ = self.base_url + str(seriesid) + '-st0-p' + str(pageindex + 1) + '-s20-isstruct0-o0.json'
                print('翻页', url_)
                yield scrapy.Request(url_ ,self.parse)

        elif response.status == 302:
            print('Retry GET '+response.url)
            yield scrapy.Request(response.url ,self.parse)

        else:
            self.index += 1
            print("[%04d] %s Failed: %s" % (self.index,response.status ,response.url))

    def wom_detail_parse(self ,response):
        # 对口碑内容进行解析
        if response.status == 200:
            data = json.loads(response.body)
            result = data['result']
            #print(response.body.decode('utf-8'))
            self.save_data(str(result['eid']) ,response.body)

        elif response.status == 302:
            print('Retry GET ' ,response.url)
            yield scrapy.Request(response.url ,self.wom_detail_parse)
        else:
            self.index += 1
            print("[%04d] Failed: %s" % (self.index ,response.url))

    def reply_parse(self ,response):
        '''
        回复内容进行解析
        :param response:
        :return:
        '''
        #print('-------------------------'+str(response.status))
        if response.status == 200:
            data = json.loads(response.body)
            # 解析出eid
            eid = re.search(r'&koubeiId=(\d+)&', response.url).group(1)  # 口碑的ID
            page_size = re.search(r'&pagesize=(\d+)&', response.url).group(1)
            # 构造规则
            # 补充：假设一个口碑有42条评论。每页page_size=20，一共有3页
            # 第一页第一条评论的位置为floor=42
            # 下一页的url，需要上一页最后一个评论的用户id来构造，即lastid
            # e.g.下面是某个口碑的几页评论
            # https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId=2543647&pagesize=20&lastid=0&hot=0
            # https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId=2543647&pagesize=20&lastid=4223200&hot=0
            # https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId=2543647&pagesize=20&lastid=4084901&hot=0
            # https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId=2543647&pagesize=20&lastid=3597607&hot=0

            first_order = data['result']['list'][0]['floor']  # 评论页面的第一个评论的顺序
            page_num = math.ceil(int(first_order)/int(page_size))
            last_comment_number = len(data['result']['list']) # 此页面一共有多少个评论
            last_user_id = data['result']['list'][last_comment_number-1]['id'] # 此页中最后一个评论的用户ID
            last_oder = data['result']['list'][last_comment_number-1]['floor'] # 还剩下多少个评论
            print("Reply"+str(eid)+'_'+str(page_num))

            self.save_data("Reply"+str(eid)+'_p'+str(page_num), response.body)

            if last_oder > 1:
                # 评论没有完，翻页
                url = 'https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId='+str(eid)+'&pagesize=20&lastid='+str(last_user_id)+'&hot=0'
                yield scrapy.Request(url, self.reply_parse)

        elif response.status == 302:
            print('Retry GET ' ,response.url)
            yield scrapy.Request(response.url,self.reply_parse)
        else:
            self.index += 1
            print("[%04d] Failed: %s" % (self.index ,response.url))

    def save_data(self ,filename ,data):
        fn = self.dir + filename
        with open(fn, 'wb') as f:
            f.write(data.decode('utf-8').encode('utf-8'))  #
            f.close()

    def get_day(self, post_time):
        '''
        将日期变化成天数。"2019-08-14" -> (2019-2000)*365+8*31+14
        其中year统一减去基数2000
        :param post_time: 日期，形式为2019-08-14"
        :return: 最后更新的天数距离坐标起点2000年已经多少天
        '''
        match = re.match(r'(\d+)-(\d+)-(\d+)', post_time)
        list_31 = ['01', '03', '05', '07', '08', '10', '12']
        list_30 = ['04', '06', '09', '11']
        list_28 = ['02']
        if match.group(2) in list_31:
            month_day = 31
        elif match.group(2) in list_30:
            month_day = 30
        else:
            month_day = 28
        return (int(match.group(1)) - 2000) * 365 + int(match.group(2)) * month_day + int(match.group(3))