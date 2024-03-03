import cSRE
import Diana
import DDSE2

from MysqlOP import MysqlOP
from BloomFilter import BloomFilter
from Util import Util

import pymongo
import time
import sys
from sys import getsizeof as getsize

from collections import defaultdict
from pathos.multiprocessing import ProcessingPool

UpCnt = defaultdict(lambda: 0)
keywords_set = dict()
value_sp = dict()
value_No = 1
max_connection = 100
upload_list_max_len = 200000


def DB_Setup(test_db_name,falut_to):
	global myclient,mydb,plaintextdb,Kc,mbf,mop,util
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	mydb = myclient["DDSE2"+test_db_name]
	plaintextdb = myclient[test_db_name]
	Diana.Setup()
	dur, Ks, Kt, Kc = DDSE2.Setup()
	util = Util()
	data_scale = util.read_scale(test_db_name)
	mbf = BloomFilter(n=data_scale,p=falut_to)
	mop = MysqlOP(test_db_name = test_db_name,max_connection_size = max_connection)

def Encrypt(h_keyword,value_set,operation):
	global mbf,util,value_No
	Keywords_Cipher = []
	keyword = 'F'+str(h_keyword)
	time_s = time.time()
	for value in value_set:
		if value not in value_sp:
			value_sp[value] = value_No
			value_No+=1
		valuein = value_sp[value]
		if operation == 'ins':
			if mbf.contains(keyword+'$'+str(valuein)) == False:
				
				mbf.add_tag(keyword+'$'+str(valuein))				
				retrieve = cSRE.Enc(h_keyword,valuein,util.hash_to_32_bytes(keyword+'$'+str(valuein)))
				dur, ct = Diana.Encrypt(keyword , UpCnt[keyword])
			else:
				
				retrieve = cSRE.Enc(h_keyword, valuein,util.hash_to_32_bytes(str(UpCnt[keyword])+keyword+'$'+str(valuein)))
				cSRE.Rev(h_keyword,util.hash_to_32_bytes(str(UpCnt[keyword])+keyword+'$'+str(valuein)))
				dur, ct = Diana.Encrypt(keyword, UpCnt[keyword])

			retrieve = util.ConvertRettoBlob(retrieve)
			Keywords_Cipher.append((ct,retrieve))
			UpCnt[keyword]+=1

		else:
			cSRE.Rev(h_keyword,util.hash_to_32_bytes(keyword+'$'+str(valuein)))

	encrypted_time = time.time() - time_s
	return encrypted_time, Keywords_Cipher


def Ciphertext_Gen_Phase():
	global plaintextdb,mop,util,Client_storage_static_bytes

	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)

	total_encrypt_time = 0
	upload_list = list()
	keyword_list = list()
	volume_list = list()
	add_time_list = list()
	Client_storage_update_bytes = list()

	for plaintext in plaintext_cur:

		h_keyword = int(plaintext['k'].replace('F',''))
		value_set = plaintext['val_set']

		bitSize,hashFuncSize = util.estimateBFsize(len(value_set), falut_to)
		cSRE.Setup(h_keyword,bitSize,hashFuncSize)

		encrypted_time, Keywords_Cipher = Encrypt(h_keyword,value_set,'ins')
		
		upload_list.extend(Keywords_Cipher)

		Client_storage_update_bytes.append(util.getupdatesize(bitSize,len([h_keyword]),len([h_keyword,value_set])))
		keyword_list.append(plaintext['k'])
		add_time_list.append(encrypted_time)
		volume_list.append(len(Keywords_Cipher))

		if len(upload_list)>= upload_list_max_len:
			mop.write_cipher_to_db(upload_list)
			upload_list = []

	if len(upload_list)> 0:
		mop.write_cipher_to_db(upload_list)
		upload_list = []

	#Write result

	resultpath = "./Result/Addtion/BF-SRE-JOIN/"+str(process_dec_num)+'/'+test_db_name+"/"
	resultname = test_group
	resulthead = ['keyword','volume','add_time','storage_update_bytes']
	resulttable = [keyword_list,volume_list,add_time_list,Client_storage_update_bytes]
	util.write_table_result(resultpath,resultname,resulthead,resulttable)

	return 

def deletion_phase_with_search(l_del_rate):
	global plaintextdb,mop,util
	
	if l_del_rate == 0:
		Search_Phase(l_del_rate)
		return

def complex_process_dec(h_keyword,skR,dec_list,process_dec_num):
	result = []
	all_task = []
	pool = ProcessingPool(process_dec_num)
	sector = 0
	slen = len(dec_list)// process_dec_num
	for i in range(len(dec_list)):
		if i == sector+slen and i!= len(dec_list)-1:
			all_task.append(pool.apipe(cSRE.DecG,h_keyword,skR,dec_list[sector:slen]))
			sector += slen
		if i == len(dec_list)-1 :
			all_task.append(pool.apipe(cSRE.DecG,h_keyword,skR,dec_list[sector:]))
	all_task = [e.get() for e in all_task]
	for res in all_task:
		result.extend(res)
	return result

def Search(keyword):
	global UpCnt,mop,util
	#the client
	h_keyword = int(keyword.replace('F',''))
	if keyword not in UpCnt:
		return 0, ""

	time_s = time.time()
	Conter = UpCnt[keyword]
	dur, k2, kc, kdepth = Diana.Trapdoor(keyword, Conter)
	skR = cSRE.sKey(h_keyword)
	time_e = time.time()
	time_user = time_e-time_s

	# the server 
	clause_list = []

	time_s = time.time()

	for i in range(Conter):
		dur, ctcheck = Diana.Search(i, k2, kc, kdepth)
		clause_list.append(ctcheck)

	result = mop.complex_thread_find(clause_list)
	result = [util.ConvertBlobtoRet(r) for r in result]
	output = []

	if process_dec_num == 0:
		output = cSRE.Dec(h_keyword,skR,result)
	else :
		output = complex_process_dec(h_keyword,skR,result,process_dec_num)
	
	time_e = time.time()
	time_server = time_e-time_s

	Client_bytes = getsize(k2)+getsize(kc)+getsize(skR)
	Server_bytes = getsize(result)
	return time_server,time_user, output, Client_bytes, Server_bytes


def Search_Phase(l_del_rate):
	global plaintextdb,util
	keyword_list = list()
	Search_keyword = list()
	Client_search = list()
	result_len = list()
	Total_search = list()
	comm_len = list()

	#Read Join query task for the afore search on the Crime dataset
	search_col = plaintextdb["id_keyword_search_list_dis"]
	plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
	task_search = [[x["Search_from"],x["Search_to"]] for x in plaintext_cur]

	for Fname, keywords in task_search:
		acc_len = 0
		acc_time = 0
		acc_commu = 0
		for keyword in keywords:
			time_server,time_user, S, Client_bytes, Server_bytes = Search(keyword)
			acc_commu+= Client_bytes+Server_bytes
			acc_time += time_server+time_user
			acc_len  += len(S)


		keyword_list.append(Fname)
		result_len.append(acc_len)
		Total_search.append(acc_time)
		comm_len.append(acc_commu)

	print(l_del_rate,"success")
	#Write result


	resulthead = ['Keyword','Total_search', 'result_len','comm_len']
	resultname = test_group
	resulttable = [keyword_list,Total_search,result_len,comm_len] 
	resultpath = "./Result/Search/BF-SRE-JOIN/"+str(process_dec_num)+'/'+test_db_name+"/d"+ str(l_del_rate) +'/'

	util.write_table_result(resultpath,resultname,resulthead,resulttable)


def Test():
	print ('*********************************************')
	print ('start test_group', test_group)
	print('start initial db')
	DB_Setup(test_db_name,falut_to)
	if 'c' in test_phase:
		Ciphertext_Gen_Phase()
	if 's' in test_phase:
		deletion_phase_with_search(del_rate)


if __name__ == "__main__":

	test_db_name = str(sys.argv[1])
	test_phase = str(sys.argv[2])
	test_group = str(sys.argv[3])
	del_rate = int(sys.argv[4])
	process_dec_num = int(sys.argv[5])
	falut_to = 0.0001
	Test()

