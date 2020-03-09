# -*-encoding:utf-8-*-
import scrapy
import json
import codecs
import re
import math
from pathlib import Path
from items import KoubeiItem
from items import WomItem
#设置将python的默认编码，一般设置为utf8的编码格式
# 这是Python2的解决办法
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')
# python3的解决办法
import importlib,sys
importlib.reload(sys)

class AppendSpider(scrapy.Spider):
    name = 'append_koubei'
    print('spider：',name)
    handle_httpstatus_list = [302 ,404 ,403 ,500 ,503]
    # https://koubei.app.autohome.com.cn/autov8.8.5/alibi/seriesalibiinfos-pm2-ss135-st0-p1-s20-isstruct1-o0.json
    #口碑列表
    base_url = "https://koubei.app.autohome.com.cn/autov8.8.5/alibi/seriesalibiinfos-pm2-ss"
    #单条口碑
    wom_base_url = "https://koubei.app.autohome.com.cn/autov8.8.5/alibi/NewEvaluationInfo.ashx?eid="
    #单条口碑对应的评论
    reply_url="http://reply.autohome.com.cn/ShowReply/ReplyJsonredis.ashx?"  #count=5&page=2&id=1344220"
    reply_url_ext="&datatype=json&appid=5"
    dir = 'E:/Do it/Python/autohome/autohome/data_koubei/' #'../data_koubei/'
    id_list = [x[:-1] for x in open('data_car_id/car_id.txt' ,'r').readlines()]  # 打开文件，读取相应的行，并且用x[:-1]处理掉'/n'
    print(id_list)
    #start_urls = [base_url + car_model_id + '-st0-p1-s20-isstruct1-o0.json' for car_model_id in id_list] #TODO 报错：name 'base_url' is not defined
    start_urls = []
    for car_model_id in id_list:
        base_url = "https://koubei.app.autohome.com.cn/autov8.8.5/alibi/seriesalibiinfos-pm2-ss"
        start_urls.append(base_url + car_model_id + '-st0-p1-s20-isstruct1-o0.json')

    def parse(self, response):
        # 一页的口碑数据
        if response.status == 200:
            data = json.loads(response.body)
            result = data['result']
            pageindex = result['pageindex']
            pagecount = result['pagecount']
            seriesid = result['seriesid']
            wom_list = result['list']
            #print(pageindex   pagecount)
            for wom in wom_list:
                koubeiid = wom['Koubeiid']
                #medals_name = wom['medals']['name'] #TODO 口碑的质量“满级”“超级满级”
                #medals_type = wom['medals']['type']
                wom_url = self.wom_base_url + str(koubeiid)
                yield scrapy.Request(wom_url,self.wom_detail_parse)

            filename = response.url.split('/')[-1]
            # TODO 一页的口碑文件原来已经有了，不需要进行修改
            #self.save_data(filename,response.body)

            if pageindex < pagecount:
                #print(pageindex ,pagecount,seriesid)
                url_ = self.base_url + str(seriesid) + '-st0-p' + str(pageindex + 1) + '-s20-isstruct0-o0.json'
                print('追加口碑：',url_)
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
            item = KoubeiItem()

            #TODO 当前追加的最大月数
            curr_append_month = self.get_append_months(result)

            #TODO 读取相应的eid文件，判断一下情况
            # 这个文件对应的是 原来的数据 '../data_pre/'
            file_name = 'E:/Do it/Python/koubei/wom_1/' + str(result['eid'])
            file_path = Path(file_name)
            if file_path.exists():
                # 口碑存在
                with open(file_name, 'r', encoding='utf-8') as f:
                    ret_dic = json.load(f)
                pre_result = ret_dic['result']
                pre_append_month = self.get_append_months(pre_result)

                # TODO 原来文件追加的月数<现在追加月数
                if pre_append_month < curr_append_month:
                    print('原来最久追加日期：', pre_append_month, '当前最久追加日期：', curr_append_month)
                    print('！！！追加需要重写！！')
                    self.save_data(str(result['eid']), response.body)

                # 只有口碑存在了才更新评论
                comment_num = result['commentcount']
                # TODO 对口碑评论进行重新爬取
                # 如果有评论，把评论爬取出来
                if comment_num > 0:
                    myreply_url = 'https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId=' + str(
                        result['eid']) + '&pagesize=20&lastid=0&hot=0'
                    yield scrapy.Request(myreply_url, self.reply_parse)
            else:
                # 原来这个口碑不存在，即这是一个新的口碑
                # 不对新口碑进行添加
                pass
                # 对新口碑进行添加
                # self.save_data(str(result['eid']), response.body.decode('utf-8'))

            yield item


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
            # TODO 构造规则
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
            print("Relpy"+str(eid)+'_'+str(page_num))

            #print(response.body.decode('utf-8'))
            # 把评论写进文件
            self.save_data("Relpy"+str(eid)+'_p'+str(page_num), response.body)

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
        #fn = self.dir + filename
        fn = 'E:/autohome_data/'+filename  #写到外部
        #print('文件名',filename)
        with open(fn, 'wb') as f:
            #print('*'*10)
            f.write(data.decode('utf-8').encode('utf-8'))  #
            f.close()


    def get_append_months(self, result):
        '''
        判断最近追加距离发表口碑已经多少个月了（即追加的最大月数）
        :param result: json解析后result对应的内容
        :return:
        '''
        appends_list = result['appends']
        # 只需要检查最新的一次追加即可
        if appends_list:
            append = appends_list[0]
            title = append['Title']  # 标题可能出现的三种形式：购车4年6个月后追加口碑 购车2年后追加口碑 购车6个月后追加口碑
            year = 0
            month = 0
            year_match = re.search(r'(\d+)年', title)
            month_match = re.search(r'(\d+)个月', title)
            if year_match:
                year = year_match.group(1)
            if month_match:
                month = month_match.group(1)
            #print(year, month)
            months_together = int(year) * 12 + int(month)
            #print(months_together)
        else:
            # 没有一个口碑
            months_together = 0
        return months_together
