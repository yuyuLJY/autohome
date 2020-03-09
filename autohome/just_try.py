# -*- coding: utf-8 -*-
import codecs
import os
import math

#fn = 'E:\\Do it\\Python\\autohome\\autohome\\data_koubei\\1245592.txt'
#fn = 'E:/Do it/Python/autohome/autohome/data_koubei/1245592.txt'

page_num = math.ceil(2/20)
print(page_num)

exit()
with open('yy.txt', 'w',encoding='utf-8') as f:
    print('*' * 50)
    str = '中国'
    #str = str.encode('utf-8')
    f.write(str)
    f.close()