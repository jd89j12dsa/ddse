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
import utilities
from sys import getsizeof as getsize


def DB_Setup(test_db_name):
	global myclient,plaintextdb
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	plaintextdb = myclient[test_db_name] 


def write_result(result_string,test_group,data):
	resultpath = "./Result"+ '/' + result_string + '/' + test_db_name + '/' + str(test_alpha) + '/' + str(test_axe) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'a')
	for d in data:
		filename.writelines(d)
	filename.close()

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

	#write_result("SealSetup", test_group, result)
	for i in result:
		print(i)

def Search_phase():
	global plaintextdb,seal
	search_col = plaintextdb["id_keyword_search_list"]
	plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
	x = plaintext_cur
	task_search = [x["k"] for x in plaintext_cur]

	# Top 1000 

	task_search = task_search[0:1000]	

	result_len = dict()
	result_size = dict()
	Search_time = dict()
	wiki_wl_v_off = {}
	cnt = 0

	for keyword in task_search:
		ts = time.time()
		result = seal.Search(keyword)
		result_len[keyword] = len(result)
		result_size[keyword] = getsize(result)
		wiki_wl_v_off[cnt] = len(result)
		result = list(filter(lambda x: x != '-1', result))
		result = list(set(result))
		Search_time[keyword] = time.time() - ts

	print('Search_success')
	#write_search_time(test_group,Search_time, result_len,result_size)
	#resultpath = "./Result"+ '/' + "SealSrch" + '/' + test_db_name + '/' + str(test_alpha) + '/' + str(test_axe) + '/'
	#utilities.dump_data_to_file(wiki_wl_v_off,resultpath,"wiki_wl_v_off.pkl")
	print('Rep. Kword result-\t', "Search_time: ", str(Search_time[task_search[0]]), '\tComm. cost: ', str(result_size[task_search[0]]) + '\n')

def write_search_time(test_group,Search_time, result_len,result_size):
	
	resultpath = "./Result"+ '/' + "SealSrch" + '/' + test_db_name + '/' + str(test_alpha) + '/' + str(test_axe) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	
	filename = open( resultpath + str(test_group),'w')

	for ke in Search_time:
		filename.writelines('keyword:\t'+str(ke) +'\t'+ str(Search_time[ke])+ '\t' +  str(result_len[ke]) + '\t' +str(result_size[ke]/1024) + 'KB' + '\n')
	filename.close()


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
	test_alpha = int(sys.argv[3])
	test_axe = int(sys.argv[4])

	Test(test_db_name,test_alpha,test_axe)
