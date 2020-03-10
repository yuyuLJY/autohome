# -*- coding: utf-8 -*-
import json
import pandas as pd
from pathlib import Path
import re
import math
import os

def get_day(str):
    '''
    将日期变化成天数。"2019-08-14" -> (2019-2000)*365+8*31+14
    其中year统一减去基数2000
    :param str: 日期，形式为2019-08-14"
    :return: 最后更新的天数距离坐标起点2000年已经多少天
    '''
    match = re.match(r'(\d+)-(\d+)-(\d+)', str)
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

def get_time_comment(car_model_id,path,name):
    '''
    功能：读取文件的口碑页文件，将日期、口碑评论数量提取出来。
    最多允许口碑页文件，缺失两块
    运行后生成两个文件：
    car_page_num.csv: 记录每个汽车id有多少页口碑。如果某辆汽车的口碑页数很少，查看是否是口碑页面出现了缺页问题
    day_comment.csv: 记录口碑ID，口碑的更新时间天数，口碑数量
    '''

    update_time = []
    koubei_id = []
    comment_num = []
    car_page_num = []

    for id in car_model_id:
        flag = True
        count = 1
        while flag:
            # print(count)
            if count == 1:
                # 第一页的文件 是isstruct1
                file_name = path+'seriesalibiinfos-pm2-ss' + id + '-st0-p1-s20-isstruct1-o0.json'
            else:
                file_name = path+'seriesalibiinfos-pm2-ss' + id + '-st0-p' + str(
                    count) + '-s20-isstruct0-o0.json'
            # 判断路径是否存在
            file_path = Path(file_name)
            if file_path.exists():
                with open(file_name, 'r', encoding='utf-8') as f:
                    ret_dic = json.load(f)

                for i in ret_dic['result']['list']:  # 结果 <class 'dict'>
                    # "posttime":"2019-08-14"
                    update_time.append(i['posttime'])
                    koubei_id.append(i['Koubeiid'])
                    comment_num.append(i['commentcount'])
                count += 1
            else:
                # 如果两个page文件都不见了，默认后边不再有page文件
                # 如果这一页page不存在，再试下一个page是否能成功，防止之间有一个page文件不见了
                file_name = path+'seriesalibiinfos-pm2-ss' + id + '-st0-p' + str(
                    count + 1) + '-s20-isstruct0-o0.json'
                file_path = Path(file_name)
                if file_path.exists():
                    count += 1
                else:
                    car_page_num.append(count - 1)
                    flag = False

    # 写进csv
    dict_1 = {'koubei_id': koubei_id, 'update_time': update_time, 'comment_num': comment_num}
    df1 = pd.DataFrame(dict_1)
    # 将日期转换成成天数
    df1['day'] = df1.apply(lambda x: get_day(x['update_time']), axis=1)
    columns = ['update_time', 'koubei_id', 'day', 'comment_num']
    df1.to_csv('data_koubei/'+name+'_day_comment.csv', sep=',', columns=columns,
               header=True,
               index=False,
               line_terminator="\n", encoding="utf_8_sig")

    dict_2 = {'car_id': car_model_id, "car_page_num": car_page_num}
    df2 = pd.DataFrame(dict_2)
    columns = ['car_id', 'car_page_num']
    df2.to_csv('data_koubei/'+name+'_car_page_num.csv', sep=',', columns=columns,
               header=True,
               index=False,
               line_terminator="\n", encoding="utf_8_sig")

def combine_comment(car_model_id,path,page_size):
    '''
     功能：将一个口碑的多页评论文件合并
     '''

    koubei_id = []
    comment_num = []

    for id in car_model_id:
        flag = True
        count = 1
        while flag:
            # print(count)
            if count == 1:
                # 第一页的文件 是isstruct1
                file_name = path + 'seriesalibiinfos-pm2-ss' + id + '-st0-p1-s20-isstruct1-o0.json'
            else:
                file_name = path + 'seriesalibiinfos-pm2-ss' + id + '-st0-p' + str(
                    count) + '-s20-isstruct0-o0.json'
            # 判断路径是否存在
            file_path = Path(file_name)
            if file_path.exists():
                with open(file_name, 'r', encoding='utf-8') as f:
                    ret_dic = json.load(f)

                for i in ret_dic['result']['list']:  # 结果 <class 'dict'>
                    # "posttime":"2019-08-14"
                    koubei_id.append(i['Koubeiid'])
                    comment_num.append(i['commentcount'])
                count += 1
            else:
                # 如果两个page文件都不见了，默认后边不再有page文件
                # 如果这一页page不存在，再试下一个page是否能成功，防止之间有一个page文件不见了
                file_name = path + 'seriesalibiinfos-pm2-ss' + id + '-st0-p' + str(
                    count + 1) + '-s20-isstruct0-o0.json'
                file_path = Path(file_name)
                if file_path.exists():
                    count += 1
                else:
                    flag = False

    # 对eid进行遍历,进行合并
    for i in range(len(koubei_id)):
        id = koubei_id[i]
        num = comment_num[i]
        # 口碑有评论进行合并
        comment_list = []
        flag = True
        count = 1
        if num>0 :
            while flag:
                # 对口碑评论文件进行遍历
                file_name = path + 'Reply' + str(id) + '_p' + str(count)
                print(id,count,file_name)
                file_path = Path(file_name)
                if file_path.exists():
                    with open(file_name, 'r', encoding='utf-8') as f:
                        ret_dic = json.load(f)
                        for k in ret_dic['result']['list']:
                            comment_list.append(k)
                    os.remove(file_name)  # !!!会删掉原来一页一页的评论文件！！！！
                    count += 1
                else:
                    file_name = path + 'Reply' + str(id) + '_p' + str(count + 1)
                    file_path = Path(file_name)
                    if file_path.exists():
                        count += 1
                    else:
                        flag = False

            # 将合并的口碑文件写进新的文件
            dict = {'result':comment_list}
            with open(path+'Reply'+str(id), 'wb') as f:
                f.write(str(dict).encode('utf-8'))
                f.close()

if __name__ == '__main__':
    option = 'S1' #S2
    if option=='S1':
        # TODO S1 更新数据前。获取原来口碑数据的更新天数、口碑评论数量
        # 需要传入需要更新的汽车模型、存储数据的位置、文件的名称
        car_model_id = ['314', '564', '770', '3013']
        path = 'E:/Do it/Python/koubei/wom_1/'  # 存储数据的位置
        name_type = 'pre'
        get_time_comment(car_model_id,path,name_type)
    else:
        # TODO S2 更新数据完毕后。将一个口碑的各页评论整理成一个文件
        # 需要传入需要更新的汽车模型、更新后数据的存储位置、评论的page_size
        page_size = 20
        car_model_id = ['3013']
        path = 'E:/autohome_data/'
        combine_comment(car_model_id, path, page_size)
