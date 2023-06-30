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
		a[int(x["k"].replace('F',""))] = {'count':len(list(x["val_set"])),'trend':[]}
		b[int(x["k"].replace('F',""))] = len(list(set(x["val_set"])))

	b = [b,b]
	return a,b

def Analyze():

	keyword_count_list, temp_dis_count_list = get_keyword_count_list()

	print(temp_dis_count_list)
	dump_data_to_file(temp_dis_count_list,"./","Wiki_DDSE_Size.pkl")

if __name__ == "__main__":
	Connect_DB('DSEWikiC')
	Analyze()