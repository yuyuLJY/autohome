# -*- coding: utf-8 -*-
import os


def main():
    # get_dealer_quote()
    # fetch_config_info()
    # get_car_type()
    # get_marketarticle_url()
	get_koubei()


def fetch_miss_woms():
    base_dir = 'C:\\workspace\\python\\autohome_test\\'
    filename1 = 'wom_json.txt'
    target_file = 'tmp_wom_urls.txt'
    wom_list = open(base_dir + filename1, 'r').readlines()
    for wom in wom_list:
        print('[*] TRY ',)
        with open(base_dir + target_file, 'w') as f:
            print(wom[:-1])
            f.write(wom)
            f.close()
        print('    ......\n',)
        os.system('scrapy crawl koubei -s LOG_FILE=scrapy.log')
        print('\n.........   done')

    print('[info] All Done')


def fmwfe():
    base_dir = 'C:\\Users\Y.C.S\\Desktop\\autohome_test\\'
    filename1 = 'wom_eids.txt'
    target_file = 'tmp_eids.txt'
    list_ = open(base_dir + filename1, 'r').readlines()
    while list_:
        if len(list_) > 4:
            tmp = list_[:4]
            list_ = list_[4:]
        else:
            tmp = list_
            list_ = []
        print('[*] TRY ',)
        with open(base_dir + target_file, 'w') as f:
            for x in tmp:
                print(x[:-1])
                f.write(x)
            f.close()
        print('    .   .   .   .   .   .\n',)
        os.system('scrapy crawl fetch_miss_wom -s LOG_FILE=scrapy.log')
        print('\n.........   done')

    print('[info] All Done')


def get_koubei():
    base_dir = 'C:\\workspace\\python\\autohome_test\\autohome_test\\'
    filename1 = 'car_model_id.txt'
    target_file = 'car_id.txt'
    id_list = open('data_car_id/car_model_id.txt', 'r').readlines()  # e.g. ['989\n', '975\n', '972\n', '971\n', '97\n']
    while id_list:
        # if-else是为了保证按照是按照每三个汽车id进行爬取口碑
        if len(id_list) > 3:
            tmp = id_list[:3]
            id_list = id_list[3:]
        else:
            tmp = id_list
            id_list = []
        print('[*] TRY ',)
        with open('data_car_id/car_id.txt', 'w') as f:
            for x in tmp:
                print(x[:-1],)  # 去掉换行符/n
                f.write(x)
            f.close()
        print('    ......\n',)

        #TODO 选择需要的spider  e.g. append_koubei 为更新口碑 koubei为重新爬取
        os.system('scrapy crawl append_koubei -s LOG_FILE=scrapy.log')
        print('\n.........   done')

    print('[info] All Done')



def get_dealer():
    base_dir = 'C:\\Users\Y.C.S\\Desktop\\autohome_test\\autohome_test\\'
    filename1 = 'all_dealers_url.txt'
    target_file = 'dealers_url.txt'
    list_ = open(base_dir + filename1, 'r').readlines()
    while list_:
        tmp = list_[0]
        list_ = list_[1:]
        print('[*] TRY ',)
        with open(base_dir + target_file, 'w') as f:
            print(tmp[:-1])
            f.write(tmp)
            f.close()
        print('    ......\n',)
        os.system('scrapy crawl dealer -s LOG_FILE=scrapy.log')
        print('\n.........   done')

    print('[info] All Done')


def get_dealer_quote():
    base_dir = 'C:\\Users\Y.C.S\\Desktop\\autohome_test\\autohome_test\\'
    filename1 = 'all_dealerids.txt'
    target_file = 'dealerid_list.txt'
    list_ = open(base_dir + filename1, 'r').readlines()
    while list_:
        tmp = list_[0]
        list_ = list_[1:]
        print('[*] TRY ',)
        with open(base_dir + target_file, 'w') as f:
            print(tmp[:-1])
            f.write(tmp)
            f.close()
        print('    ......\n',)
        os.system('scrapy crawl dealer_quote -s LOG_FILE=scrapy.log')
        print('\n.........   done')

    print('[info] All Done')


def fetch_config_info():
    target_file = 'tmp_id.txt'
    all_model_ids = open('all_model_ids.txt', 'r').readlines()
    for model_id in all_model_ids:
        with open(target_file, 'w') as f:
            f.write(model_id)
            f.close()
        print('[*] TRY get config info about %s.' % (model_id,))
        os.system('scrapy crawl config -s LOG_FILE=scrapy.log')
    print('\n[*] All done.')


def get_car_type():
    target_file = 'tmp_miss_car_type_ids.txt'
    all_model_ids = open('miss_car_type_ids.txt', 'r').readlines()
    for model_id in all_model_ids:
        with open(target_file, 'w') as f:
            f.write(model_id)
            f.close()
        print('[*] TRY get car_type of  %s.' % (model_id,))
        os.system('scrapy crawl cartype2 -s LOG_FILE=scrapy.log')
    print('\n[*] All done.')


def get_marketarticle_url():
    target_file = 'tmp_car_model_id.txt'
    all_model_ids = open('all_car_model_id.txt', 'r').readlines()
    for model_id in all_model_ids:
        with open(target_file, 'w') as f:
            f.write(model_id)
            f.close()
        print('[*] TRY get market article of  %s.' % (model_id,))
        os.system('scrapy crawl marketarticle -s LOG_FILE=scrapy.log')
    print('\n[*] All done.')


if __name__ == '__main__':
    main()
