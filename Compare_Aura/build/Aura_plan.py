import heapq
import sys
import os
import pdb
import time
import csv
import shutil
import math
import pymongo
from collections import defaultdict

min_val = 20000000
max_val = 40000000

def GenDBSetup(keyword_dict):

    #proceed filename and id-like
    translated_dict = defaultdict(list)
    translated_filenames_reverse = dict()
    same_mean_file = defaultdict(list)
    global_filename_cnt = 1
    global_filename_map = defaultdict(list)
    entires = 0

    for keyword, filenames in keyword_dict.items():
        translated_filenames = []
        temp_filenames_cnt = defaultdict(int)
        for filename in filenames:
            temp_filenames_cnt[filename]+=1
        dis_filenames = list(set(filenames))
        for filename in dis_filenames:
            update_num = max(0,temp_filenames_cnt[filename]-len(global_filename_map[filename]))
            for i in range(0,update_num):
                global_filename_map[filename].append(global_filename_cnt)
                translated_filenames_reverse[global_filename_cnt] = filename
                global_filename_cnt+=1
            translated_filenames.extend(global_filename_map[filename][:temp_filenames_cnt[filename]])
        translated_filenames = fill_and_remove_duplicates(translated_filenames)
        translated_dict[keyword] = translated_filenames
        entires+= len(translated_filenames)

    #pad data

    return entires,translated_dict,len(translated_filenames_reverse),translated_filenames_reverse





def closest_power_of_4(num):
    # 计算最接近的2的幂次方
    power = 0
    while 4 ** power < num:
        power += 1
    return 4 ** power

def fill_and_remove_duplicates(input_list):
    global min_val,max_val
    # 去除重复数据
    unique_list = list(set(input_list))

    # 将列表的大小扩展到最接近的4的幂次方
    target_size = closest_power_of_4(len(input_list))

    # 填充列表
    while len(unique_list) < target_size:
        unique_list.append(min_val)
        min_val += 1
        if min_val > max_val:
            break

    return unique_list[:target_size]  # 截取最终结果列表的前 target_size 个元素


def DB_read(test_db_name):

    myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
    plaintextdb = myclient[test_db_name]

    return myclient,plaintextdb


if __name__ == '__main__':

    test_db_name = str(sys.argv[1])
    myclient,plaintextdb = DB_read(test_db_name)

    plaintext_col = plaintextdb["id_keywords"]
    plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)
    plaintextdata = dict()
    for plaintext in plaintext_cur:
        plaintextdata[plaintext['k']] = plaintext['val_set']

    entries,filename_dict,rev_len,translated_filenames_reverse = GenDBSetup(plaintextdata)


    with open('./'+test_db_name+'REV','w', encoding="ascii") as file:
        file.writelines(str(rev_len)+"\n")
        for fake_cnt, real_cnt in translated_filenames_reverse.items():
            file.writelines(str(fake_cnt)+" "+str(real_cnt)+"\n")


    #pdb.set_trace()

    search_col = plaintextdb["id_keyword_search_list"]

    search_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
    task_search = [x["k"] for x in search_cur]
    task_del = task_search[0]
    plaintext_cur = plaintext_col.find_one({"k":task_del})
    del_set = plaintext_cur['val_set']

    del_len = len(del_set)

    with open('./'+test_db_name+'Search','w', encoding="ascii") as file:
        for plaintext in task_search:
            file.writelines(plaintext.replace("F","")+"\n")

    with open('./'+test_db_name+'DB','w', encoding="ascii") as file:
        file.writelines(str(entries)+"\n")
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("INS"+" "+keyword.replace("F","")+" "+str(filename)+"\n")


    with open('./'+test_db_name+'DB10','w', encoding="ascii") as file:
        file.writelines(str(entries+int(del_len*0.1))+"\n")
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("INS"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
        cnt = 0
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("DEL"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
                cnt+= 1
            if cnt > del_len*0.1:
                break

    with open('./'+test_db_name+'DB20','w', encoding="ascii") as file:
        file.writelines(str(entries+int(del_len*0.2))+"\n")
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("INS"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
        cnt = 0
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("DEL"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
                cnt+= 1
            if cnt > del_len*0.2:
                break


    with open('./'+test_db_name+'DB30','w', encoding="ascii") as file:
        file.writelines(str(entries+int(del_len*0.3))+"\n")
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("INS"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
        cnt = 0
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("DEL"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
                cnt+= 1
            if cnt > del_len*0.3:
                break


    with open('./'+test_db_name+'DB40','w', encoding="ascii") as file:
        file.writelines(str(entries+int(del_len*0.4))+"\n")
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("INS"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
        cnt = 0
        for keyword, filenames in filename_dict.items():
            for filename in filenames:
                file.writelines("DEL"+" "+keyword.replace("F","")+" "+str(filename)+"\n")
                cnt+= 1
            if cnt > del_len*0.4:
                break



