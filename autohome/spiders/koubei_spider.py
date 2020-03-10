# -*-encoding:utf-8-*-
import scrapy
import json
import math
import codecs
import re
from items import KoubeiItem
from items import WomItem
import sys
import chardet
#在Python2.x中由于str和byte之间没有明显区别，经常要依赖于defaultencoding来做转换
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

class WomSpider(scrapy.Spider):
    name = 'koubei'
    print('spider：', name)
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
    #start_urls = [base_url + car_model_id + '-st0-p1-s20-isstruct1-o0.json' for car_model_id in id_list] #TODO 报错：name 'base_url' is not defined
    start_urls = []
    for car_model_id in id_list:
        base_url = "https://koubei.app.autohome.com.cn/autov8.8.5/alibi/seriesalibiinfos-pm2-ss"
        start_urls.append(base_url + car_model_id + '-st0-p1-s20-isstruct1-o0.json')


    def parse(self, response):
        if response.status == 200:
            data = json.loads(response.body)
            result = data['result']
            pageindex = result['pageindex']
            pagecount = result['pagecount']
            seriesid = result['seriesid']
            wom_list = result['list']
            for wom in wom_list:
                koubeiid = wom['Koubeiid']
                wom_url = self.wom_base_url + str(koubeiid)
                yield scrapy.Request(wom_url,self.wom_detail_parse)

            filename = response.url.split('/')[-1]

            self.save_data(filename,response.body)
            # 口碑抓取，进行翻页
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
            item = KoubeiItem()
            item['seriesid'] = result['seriesid']
            item['brandid'] = result['brandid']
            item['powertype'] = result['powertype']
            item['powername'] = result['powername']
            item['isbattery'] = result['isbattery']
            item['userId'] = result['userId']
            item['userName'] = result['userName']
            item['specid'] = result['specid']
            item['specname'] = result['specname']
            item['boughtcityname'] = result['boughtcityname']
            item['boughtdate'] = result['boughtdate']
            item['boughtPrice'] = result['boughtPrice']
            item['actualOilConsumption'] = result['actualOilConsumption']
            item['actualBatteryConsumption'] = result['actualBatteryConsumption']
            item['drivekilometer'] = result['drivekilometer']
            item['spaceScene_score'] = result['spaceScene']['score']
            item['powerScene_score'] = result['powerScene']['score']
            item['maneuverabilityScene_score'] = result['maneuverabilityScene']['score']
            item['oilScene_score'] = result['oilScene']['score']
            item['batteryScene_score'] = result['batteryScene']['score']
            item['comfortablenessScene_score'] = result['comfortablenessScene']['score']
            item['apperanceScene_score'] = result['apperanceScene']['score']
            item['internalScene_score'] = result['internalScene']['score']
            item['costefficientScene_score'] = result['costefficientScene']['score']
            purpose = ""
            for p in result['purpose']:
                purpose += p['purposename']

            item['purpose'] = purpose
            item['eid'] = result['eid']
            item['created'] = result['created']

            yield item
            self.save_data(str(result['eid']) ,response.body)

            comment_num = result['commentcount'] #评论的个数
            # 如果有评论，把评论爬取出来
            if comment_num > 0:
                myreply_url = 'https://koubei.app.autohome.com.cn/autov9.13.0/news/KouBeiComments.ashx?pm=1&koubeiId='+str(result['eid'])+'&pagesize=20&lastid=0&hot=0'
                yield scrapy.Request(myreply_url,self.reply_parse)

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

            #print(response.body.decode('utf-8'))
            # 把评论写进文件
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

    def loads_jsonp(_jsonp):
        try:
            return json.loads(re.match(".*?({.*}).*",  _jsonp,  re.S).group(1))
        except:
            raise ValueError('Invalid Input')

    def save_data(self ,filename ,data):
        #fn = self.dir + filename
        #print('文件名',filename)
        fn = 'E:/autohome_data/' + filename  # 写到外部
        with open(fn, 'wb') as f:
            #print('*'*10)
            f.write(data.decode('utf-8').encode('utf-8'))  #
            f.close()


