import DianaM
import MITRAPP
import pymongo
import time
import pdb
import sys
import os
from sys import getsizeof
import threading

from MysqlOP import MysqlOP
from Util import Util
from Padding import Padding

from collections import defaultdict


max_connection = 100
upload_list_max_len = 200000
keyword_counter = dict()


def DB_Setup(test_db_name):
	global myclient,plaintextdb,ownerkey,data_scale,mop,util,padding
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	mydb = myclient["MITRAPP"+test_db_name]
	plaintextdb = myclient[test_db_name]
	dur, ownerkey,_,_ = DianaM.Setup()
	mop = MysqlOP(test_db_name, max_connection)
	util = Util()
	data_scale = util.read_scale(test_db_name)
	padding = Padding()

def Encrypt(keyword,value_set,operation):
	global ownerkey
	encrypted_time = 0
	Keywords_Cipher = []
	for value in value_set:
		time_s = time.time()
		if keyword not in keyword_counter:
			keyword_counter[keyword] = 0

		plain = str(value)+'$'+str(keyword_counter[keyword])+operation
		plain = plain+ "".join(['%' for x in range(0,(16-len(plain)%16))])
		#pdb.set_trace()
		dur, session = MITRAPP.PRF(ownerkey,keyword)
		dur, retrievecipher = MITRAPP.AESEncrypt(session,plain)
		#pdb.set_trace()
		dur, ct1=DianaM.Encrypt(keyword , keyword_counter[keyword])
		ct2 = retrievecipher
		keyword_counter[keyword] +=1
		time_e = time.time()
		encrypted_time += (time_e - time_s)
		Keywords_Cipher.append((ct1,ct2))

	return encrypted_time, Keywords_Cipher



def Ciphertext_Gen_Phase():
	global plaintextdb,data_scale,padding,mop,util

	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)

	keyword_list = list()
	volume_list = list()
	add_time_list = list()
	Client_storage_update_bytes = list()


	total_encrypt_time = 0
	entry_counter = 0
	result = []
	upload_list = []
	for plaintext in plaintext_cur:
		padded_set = padding.fill(plaintext['val_set'])
		encrypted_time , Keywords_Cipher = Encrypt(plaintext['k'],padded_set,'ins')
		upload_list.extend(Keywords_Cipher)


		keyword_list.append(plaintext['k'])
		volume_list.append(len(Keywords_Cipher))
		add_time_list.append(encrypted_time)
		Client_storage_update_bytes.append(util.getupdatesize(0,0,len([padded_set])))

		if len(upload_list)>= upload_list_max_len:
			mop.write_cipher_to_db(upload_list)
			upload_list = []

	if len(upload_list)>= 0:
		mop.write_cipher_to_db(upload_list)
		upload_list = []


	resultpath = "./Result/Addtion/MITRAPP/"+test_db_name+"/"
	resultname = test_group
	resulthead = ['keyword','volume','add_time','storage_update_bytes']
	resulttable = [keyword_list,volume_list,add_time_list,Client_storage_update_bytes]
	util.write_table_result(resultpath,resultname,resulthead,resulttable)

	return


def Deletion_phase_with_search(l_del_rate):

	global plaintextdb,data_scale,mop

	search_col = plaintextdb["id_keyword_search_list"]
	search_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
	task_search = [x["k"] for x in search_cur]
	task_del = task_search[0]

	sector_del_num = data_scale//10

	if l_del_rate == 0:
		Search_Phase(l_del_rate)
		return		

	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)

	del_list = []
	for plaintext in plaintext_cur:
		keyword = plaintext['k']
		val_set = plaintext['val_set']
		for i in val_set:
			del_list.append([keyword,i])
		if len(del_list) >= sector_del_num*l_del_rate:
			break

	calc_list = del_list[0:l_del_rate*sector_del_num]

	merged = defaultdict(list)
	for i in calc_list:
		merged[i[0]].append(i[1])

	del_time = 0
	upload_list = []

	for keyword in merged:
		encrypted_time , Keywords_Cipher = Encrypt(keyword,merged[keyword],'del') 
		upload_list.extend(Keywords_Cipher)
		del_time += encrypted_time
		if len(upload_list)>= upload_list_max_len:
			mop.write_cipher_to_db(upload_list)
			upload_list = []

	if len(upload_list)>= 0:
		mop.write_cipher_to_db(upload_list)
		upload_list = []

	Search_Phase(l_del_rate)

def Search(keyword):
	global keyword_counter
	result = []
	time_s = time.time()
	if keyword not in keyword_counter:
		return 0, ""
	Conter = keyword_counter[keyword]
	dur, k2, kc, kdepth = DianaM.Trapdoor(keyword, Conter)
	time_e = time.time()
	clause_list = []
	for i in range(Conter):
		dur, ctcheck = DianaM.Search( i, k2, kc, kdepth)
		clause_list.append(ctcheck)

	result = mop.complex_thread_find(Conter,clause_list)

	return time_e-time_s, result

def Search_Phase(l_del_rate):
	global ownerkey,plaintextdb,padding,mop,util # wait for writing log file

	keyword_list = list()
	Client_search = list()
	Total_search = list()
	comm_len = list()
	result_len = list()

	search_col = plaintextdb["id_keyword_search_list"]
	plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
	task_search = [x["k"] for x in plaintext_cur]


	if l_del_rate > 0:
		task_search = task_search[0:1]

	for keyword in task_search:
		time_s = time.time()
		client_time,re = Search(keyword)

		#pdb.set_trace()
		search_result = []
		time_s_2 = time.time()
		dur,session = MITRAPP.PRF(ownerkey,keyword)
		for y in re:
			dur, x = MITRAPP.AESDecrypt(session,y)
			#pdb.set_trace()
			x = x.replace("%","")
			p = x.split("$")[0]
			# pdb.set_trace()
			if x[-3:] == 'ins' :
				search_result.append(p)
				search_result = list(set(search_result))
			if x[-3:] == 'del' and p in search_result:
				search_result.remove(p)

		#reencrypt to db
		true_search_result = padding.eliminate_dummy(search_result)
		padded_set = padding.fill(true_search_result)
		encrypted_time , Keywords_Cipher = Encrypt(keyword,padded_set,'ins')
		mop.write_cipher_to_db_2(Keywords_Cipher)
		time_e = time.time()

		client_time += time_e-time_s_2
		total_search_time = time_e-time_s

		keyword_list.append(keyword)
		result_len.append(len(re) + len(Keywords_Cipher))
		Client_search.append(client_time)
		Total_search.append(total_search_time)
		comm_len.append(sum([sys.getsizeof(rei) for rei in re]) + sum([sys.getsizeof(Keyw[0])+sys.getsizeof(Keyw[1]) for Keyw in Keywords_Cipher]))

	print(l_del_rate,"success")

	resulthead = ['Keyword','Client_Search_time','Total_search', 'result_len','comm_len']
	resultname = test_group
	resulttable = [keyword_list,Client_search,Total_search,result_len,comm_len] 
	resultpath = "./Result/Search/MITRAPP/"+test_db_name+"/d"+ str(l_del_rate) +'/'

	util.write_table_result(resultpath,resultname,resulthead,resulttable)


def Test():
	l = list(test_phase)
	print ('*********************************************')
	print ('test_on ', test_db_name, 'del_rate ', del_rate)
	print ('start test_group ', test_group)
	print('start initial db')
	DB_Setup(test_db_name)
	if 'c' in test_phase:
		Ciphertext_Gen_Phase()
	if 's' in test_phase:
		Deletion_phase_with_search(del_rate)

if __name__ == "__main__":

	test_db_name = str(sys.argv[1])
	test_phase = str(sys.argv[2])
	test_group = str(sys.argv[3])
	del_rate = int(sys.argv[4])
	Test()

	
