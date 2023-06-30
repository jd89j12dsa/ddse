#coding=utf-8
import pymongo
import sys
import os
import pickle
from collections import defaultdict

def Connect_DB(test_db_name):
	global myclient, mydb, mydata,mysearch
	myclient = pymongo.MongoClient("mongodb://localhost:27017/")
	mydb = myclient[test_db_name]
	mydata = mydb["id_keywords"]
	mysearch = mydb["id_keyword_search_list"]

def dump_data_to_file(data,key_folder, filename):
    f = open(os.path.join(key_folder, filename),"wb")
    pickle.dump(data,f)
    f.close()

def get_keyword_count_list():
	global mydata,mysearch
	a = dict()
	b = dict()
	for x in mydata.find():
		a[x["k"]] = {'count':len(list(x["val_set"]))}
		b[x["k"]] = len(list(set(x["val_set"])))

	return a,b

def get_keyword_distinct_count_list(keyword_count_list,temp_dis_count_list):
	global mysearch
	a = dict()
	c = dict()
	cnt = 0
	for x in mysearch.find():
		c[x["k"]] = keyword_count_list[x["k"]]
		a[cnt] = temp_dis_count_list[x["k"]]
		cnt += 1

	b = [a,a]
	return c,b

def Analyze():

	keyword_count_list, temp_dis_count_list = get_keyword_count_list()
	keyword_count_list,keyword_distinct_count_list = get_keyword_distinct_count_list(keyword_count_list,temp_dis_count_list)

	dump_data_to_file(keyword_count_list,"./","wiki_kws_dict.pkl")

	dump_data_to_file(keyword_distinct_count_list,"./","Wiki_DDSE_Size.pkl")



if __name__ == "__main__":
	Connect_DB('DSEWikiC')
	Analyze()