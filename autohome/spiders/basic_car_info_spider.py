#--coding: utf-8--
import scrapy
import json
import copy
import re
import pandas as pd
from items import CarbasicInfo

# **爬取汽车（分类/ID/国籍/价格）等基本信息**
class BasicCarInfoSpider(scrapy.Spider):
    name = 'basic_car_infomation'
    #allowed_domains = ['douban.com']
    #start_urls = ['https://k.autohome.com.cn/850/'] #必须以

    def start_requests(self):
        '''
        逐个进行遍历汽车的类型
        :return:
        '''

        cookie = {
            'cookie': 'fvlid=15731275004289VzrJikKIu; sessionid=25689CE1-478A-44A1-AFE8-C2F6481AEEF3%7C%7C2019-11-07+19%3A51%3A40.749%7C%7Cwww.baidu.com; autoid=72d37dc06a11256e440647ddcd349b88; area=230103; sessionuid=25689CE1-478A-44A1-AFE8-C2F6481AEEF3%7C%7C2019-11-07+19%3A51%3A40.749%7C%7Cwww.baidu.com; guidance=true; pcpopclub=6439b46aae594468a95c7ce8f3aba6790a764047; clubUserShow=175521863|0|230100|an5c2ptrk48|0|0|0||2019-11-17 19:20:07|2; autouserid=175521863; __ah_uuid_ng=u_175521863; __utma=1.1872434172.1573989454.1573989454.1574055209.2; __utmz=1.1574055209.2.2.utmcsr=i.autohome.com.cn|utmccn=(referral)|utmcmd=referral|utmcct=/37952320/photo; sessionip=219.217.246.197; ahpau=1; Hm_lvt_9924a05a5a75caf05dbbfb51af638b07=1576139922; sessionlogin=80c9fd0da10c473cbb95d48e50b5a2f50a764047; sessionuserid=175521863; ASP.NET_SessionId=ozmhlzsecvds04fi4x1dzdgg; sessionvid=3E5A5DFC-7691-4A42-A1E9-518576138C04; pvidchain=2112108,2112108; video-46-0=46EF3AC6D52B85B9; v_no=178; ref=www.baidu.com%7C0%7C0%7C0%7C2019-12-15+21%3A03%3A29.311%7C2019-11-07+19%3A51%3A40.749; autoac=860870D45A741BD87601710F44548E7B; autotc=BA5D82B768E0DE0F3A4A63AF64A58E18; ahpvno=12',
            'Referer':'https://k.autohome.com.cn/suvc1/'
        }

        car_type = ["a00", "a0", "a", "b", "c", "d", "suv", "mpv", "s", "p", "mb", "qk"]  #12
        nation_type = ['1','2','3','4','5','6','7','8','11']  # 1中国 2德国 3日系 4美 5韩系 6法国 7英国 8意大利  11捷克

        # 组合url
        all_car_urls = []
        for i in car_type:
            for j in nation_type:
                all_car_urls.append('https://www.autohome.com.cn/'+i+'/0_0-0.0_0.0-0-0-0-0-0-'+j+'-0-0/')

        for i in range(len(all_car_urls)):
            #对每一款类型的车进行遍历
            print('*'*20,i,'*'*20)
            print('爬取汽车：',all_car_urls[i])
            yield scrapy.Request(url=all_car_urls[i],
                                 meta={
                                     'dont_redirect': True,
                                     'handle_httpstatus_list': [302]
                                 },
                                 callback=self.parse, cookies=cookie)

    def parse(self, response):
        #把下一页的页码解析出来
        print('进行解析')
        item = CarbasicInfo()
        # alphabet_list
        # --company_list
        # ----car_brand
        #
        #
        alphabet_list = response.xpath("//div[@class='uibox-con rank-list rank-list-pic']")
        url = response.url

        #TODO
        nation_id = re.search(r'0_0-0.0_0.0-0-0-0-0-0-(\d+)-0-0', url).group(1)
        type_id = re.search(r'.cn/(.*?)/0', url).group(1)
        type_dict = {"a00":"微型车", "a0":"小型车", "a":"紧凑型车", "b":"中型车", "c":"中大型车", "d":"大型车", "suv":"suv", "mpv":"mpv", "s":"跑车", "p":"皮卡", "mb":"微面", "qk":"轻客"}
        nation_dict = {'1':'中国','2':'德国' ,'3':'日系' ,'4':'美', '5':'韩系' ,'6':'法国', '7':'英国', '8':'意大利' , '11':'捷克'}  # 1中国 2德国 3日系 4美 5韩系 6法国 7英国 8意大利  11捷克
        nation_name = nation_dict[nation_id]
        type_name = type_dict[type_id]
        print(nation_name,type_name)
        for i in alphabet_list:
            #print(i)
            company_list = i.xpath(".//dl")
            for j in company_list:
                #print(j)
                company_bigtype = j.xpath(".//dt/div/a/text()").extract()[0] #大类的名称
                item['company_bigtype'] = company_bigtype
                item['car_company'] = j.xpath(".//dd/div[@class='h3-tit']/a/text()").extract()[0] #
                each_campany_car = j.xpath(".//dd/ul[@class='rank-list-ul']/li[contains(@id,'s')]") #汽车企业下的每款车子
                for k in each_campany_car:
                    car_brand_url = k.xpath(".//h4/a/@href").extract()[0]#解析出id
                    item['car_brand_id'] = re.findall(r"\d+", car_brand_url)[0]
                    # 不一定有指导价格
                    if str(k.xpath(".//div[1]/text()").extract()[0]).__contains__('暂无'):
                        item['price'] = ''
                    else:
                        item['price'] = k.xpath(".//div[1]/a/text()").extract()[0]

                    item['car_brand'] = k.xpath(".//h4/a/text()").extract()[0]
                    item['nation_name'] = nation_name
                    item['type_name'] = type_name
                    yield item
        #TODO 未检查是否有第二页，如果有翻页需要翻页处理


