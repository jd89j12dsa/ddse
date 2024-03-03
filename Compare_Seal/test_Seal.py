from Seal import Seal
import pymongo
import time
import sys
import json
import random
import threading
import pdb
import math
import os
import faulthandler
from Util import Util
from sys import getsizeof as getsize


def DB_Setup(test_db_name):
	global myclient,plaintextdb
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	plaintextdb = myclient[test_db_name] 

def Setup_phase(test_alpha,test_axe):

	global plaintextdb,seal
	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)
	Dataset = dict()

	for plaintext in plaintext_cur:
		Dataset[plaintext['k']] = plaintext['val_set']

	ts = time.time()

	seal = Seal(test_alpha, test_axe)
	padt, stt, updatet = seal.Setup(Dataset)

	result = []
	result.append("pad time:\t"+str(padt)+"\n")
	result.append("sett time:\t"+ str(stt)+"\n")
	result.append("updatet time:\t"+ str(updatet)+"\n")

	for i in result:
		print(i)

def Search_phase():
	global plaintextdb,seal,util
	search_col = plaintextdb["id_keyword_search_list"]
	plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
	x = plaintext_cur
	task_search = [x["k"] for x in plaintext_cur]

	keyword_set = list()
	result_len = list()
	result_size = list()
	Search_time = list()

	for keyword in task_search:
		ts = time.time()
		result,result_S = seal.Search(keyword)		
		result1 = list(filter(lambda x: x != '-1', result))
		result1 = list(set(result1))

		Search_time.append(time.time() - ts)
		keyword_set.append(keyword)
		result_len.append(len(result))
		result_size.append(result_S)

	resulthead = ['Keyword','Total_search', 'result_len','comm_len']
	resultname = test_group
	resulttable = [keyword_set,Search_time,result_len,result_size] 
	resultpath = "./Result/Search/Seal/"+test_db_name+'/'

	util.write_table_result(resultpath,resultname,resulthead,resulttable)

def Test(test_db_name,test_alpha,test_axe):

	print('-----------Test Seal Comparsion-----------')

	print('test_group: ',test_group,'test_db_name: ',test_db_name,'test_alpha: ',test_alpha,'test_axe: ',test_axe)

	DB_Setup(test_db_name)
	Setup_phase(test_alpha,test_axe)
	Search_phase()	

if __name__ == '__main__':

	faulthandler.enable()
	test_db_name = str(sys.argv[1])
	test_group = str(sys.argv[2])
	test_alpha = 20
	test_axe = 4

	util = Util()

	Test(test_db_name,test_alpha,test_axe)
