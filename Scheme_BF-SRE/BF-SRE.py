import cSRE
import Diana
import DDSE2
from MysqlOP import MysqlOP
from BloomFilter import BloomFilter

import pymongo
import time
import sys
from sys import getsizeof as getsize
import os
import pdb
from collections import defaultdict
from pathos.multiprocessing import ProcessingPool
import json
import base64
import math
import hashlib

UpCnt = defaultdict(lambda: 0)
keywords_set = dict()
value_sp = dict()
value_No = 1
max_connection = 100
upload_list_sector = 10000
upload_list_max_len = 200000
# check556bf =  []

def hash_to_32_bytes(input_string):
    md5_hash = hashlib.md5()
    input_bytes = input_string.encode('utf-8')
    md5_hash.update(input_bytes)
    return md5_hash.hexdigest()

def DB_Setup(test_db_name,data_scale,falut_to):
	global myclient,mydb,plaintextdb,ownerkey,Ks,Kt,Kc,mbf,mop
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	mydb = myclient["DDSE2"+test_db_name]
	plaintextdb = myclient[test_db_name] 
	dur, ownerkey, keyleft, keyright = Diana.Setup()
	dur, Ks, Kt, Kc = DDSE2.Setup()
	mbf = BloomFilter(n=data_scale,p=falut_to)
	mop = MysqlOP(test_db_name = test_db_name,max_connection_size = max_connection)

def Encrypt(keyword,value_set,operation):
	global mbf,value_No
	Keywords_Cipher = []
	h_keyword = int(keyword.replace('F',''))
	if h_keyword not in keywords_set:
		n = len(value_set)
		p = falut_to
		bitSize=int(-n*math.log(p)/math.pow(math.log(2),2))
		hashFuncSize=int(bitSize*math.log(2)/n)
		cSRE.Setup(h_keyword,min(600000,bitSize),hashFuncSize)
		keywords_set[h_keyword] = 1
	time_s = time.time()
	
	for value in value_set:
		if value not in value_sp:
			value_sp[value] = value_No
			value_No+=1
		valuein = value_sp[value]
		if operation == 'ins':
			if mbf.contains(keyword+'$'+str(valuein)) == False:
				# if keyword == 'F556':
				# 	check556bf.append(0)
				mbf.add_tag(keyword+'$'+str(valuein))				
				retrieve = cSRE.Enc(h_keyword,valuein,hash_to_32_bytes(keyword+'$'+str(valuein)))
				dur, ct = Diana.Encrypt(keyword , UpCnt[keyword])
			else:
				# if keyword == 'F556':
				# 	check556bf.append(1)
				retrieve = cSRE.Enc(h_keyword, valuein, hash_to_32_bytes(str(UpCnt[keyword])+keyword+'$'+str(valuein)))
				cSRE.Rev(h_keyword, hash_to_32_bytes(str(UpCnt[keyword])+keyword+'$'+str(valuein)))
				dur, ct = Diana.Encrypt(keyword, UpCnt[keyword])

			retrieve = ConvertRettoBlob(retrieve)
			Keywords_Cipher.append((ct,retrieve))
			UpCnt[keyword]+=1

		else:
			cSRE.Rev(h_keyword, hash_to_32_bytes(keyword+'$'+str(valuein)))

	encrypted_time = time.time() - time_s
	return encrypted_time, Keywords_Cipher



def Ciphertext_Gen_Phase():
	global plaintextdb,mop

	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)

	total_encrypt_time = 0
	entry_counter = 0
	sector = upload_list_sector
	result = []
	upload_list = []
	for plaintext in plaintext_cur:
		encrypted_time, Keywords_Cipher = Encrypt(plaintext['k'],plaintext['val_set'],'ins')
		write_volume_update(plaintext['k'],encrypted_time,len(plaintext['val_set']))
		entry_counter += len(Keywords_Cipher)
		total_encrypt_time += encrypted_time
		if entry_counter >= sector:
			sector += upload_list_sector
			result.append('len:\t'+str(entry_counter) +'\t'+ str(total_encrypt_time)+'\n')
			if len(result) > 10:
				if process_dec_num == 0:
					write_result_G("DDSE2Add",test_group,result,0)
				else:
					write_result_P("DDSE2Add",test_group,result,0)
				result = []
		upload_list.extend(Keywords_Cipher)
		if len(upload_list)>= upload_list_max_len:
			print("start slice")
			mop.write_cipher_to_db(upload_list)
			upload_list = []

	if len(upload_list)> 0:
		mop.write_cipher_to_db(upload_list)
		upload_list = []
	if len(result) > 0:
		if process_dec_num == 0:
			write_result_G("DDSE2Add",test_group,result,0)
		else:
			write_result_P("DDSE2Add",test_group,result,0)
	return 

def deletion_phase_with_search(l_del_num,l_del_rate):
	global plaintextdb,ciphercol,mop
	
	search_col = plaintextdb["id_keyword_search_list"]
	plaintext_col = plaintextdb["id_keywords"]

	search_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
	task_search = [x["k"] for x in search_cur]
	task_del = task_search[0]
	plaintext_cur = plaintext_col.find_one({"k":task_del})
	del_set = plaintext_cur['val_set']
	# pdb.set_trace()
	if l_del_rate == 0:
		Search_Phase(l_del_num,l_del_rate)
	else:
		start_node = 0
		for j in range(l_del_rate+1):
			Search_Phase(l_del_num,j)

			if start_node+l_del_num > len(del_set):
				print('bad_del_len')
				break
			encrypted_time, Keywords_Cipher = Encrypt(task_del,del_set[start_node:l_del_num],'del')
			result = ['del_num:\t'+str(len(Keywords_Cipher))+'\t'+str(encrypted_time)+'\n',]
			start_node+=l_del_num
			if process_dec_num == 0:
				write_result_G("DDSE2Del",test_group,result,j)
			else:
				write_result_P("DDSE2Del",test_group,result,j)
						


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
	global UpCnt,mop
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
	time_s = time.time()
	result = [ConvertBlobtoRet(r) for r in result]
	#pdb.set_trace()
	output = []
	if process_dec_num == 0:
		output = cSRE.Dec(h_keyword,skR,result)
	else :
		output = complex_process_dec(h_keyword,skR,result,process_dec_num)
	# print(keyword,output)
	# pdb.set_trace()

	time_e = time.time()
	time_server = time_e-time_s
	#if keyword not in EDB_cache:
	Client_bytes = getsize(k2)+getsize(kc)+getsize(skR)
	Server_bytes = getsize(result)
	return time_server,time_user, output, Client_bytes, Server_bytes


def Search_Phase(l_del_num,l_del_rate):
	global mydb,ownerkey,mydb,plaintextdb
	search_result = []
	Search_time = dict()
	result_len = dict()
	total_time = dict()
	Client_bytes_len = dict()
	Server_bytes_len = dict()
	Search_Phase_time = 0

	if l_del_rate == 0:
		search_col = plaintextdb["id_keyword_search_list"]
		plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
		task_search = [x["k"] for x in plaintext_cur]
		
	else:
		search_col = plaintextdb["id_keyword_search_list"]
		plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
		task_search = [x["k"] for x in plaintext_cur]
		task_search = task_search[0:1]

	for keyword in task_search:
		# pdb.set_trace()
		time_server,time_user, S, Client_bytes, Server_bytes = Search(keyword)

		result_len[keyword] = len(S)
		Search_time[keyword] = time_server
		total_time [keyword] = time_server+time_user
		Client_bytes_len[keyword] = Client_bytes
		Server_bytes_len[keyword] = Server_bytes

	print(l_del_num*l_del_rate,"success")

	if process_dec_num == 0:
		write_search_time_G(test_group,Search_time,total_time, result_len,Client_bytes_len,Server_bytes_len,l_del_num*l_del_rate)
	else:
		write_search_time_P(test_group,Search_time,total_time, result_len,Client_bytes_len,Server_bytes_len,l_del_num*l_del_rate)



def write_volume_update(keyword,uptime,volume):
	resultpath = "./Result"+ '/' + 'Volume_update' + '/' + test_db_name + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	d = str(keyword) + '\t' + str(volume) + '\t' + str(uptime) + '\n' 
	filename = open(resultpath + str(test_group),'a')
	filename.writelines(d)
	filename.close()



def write_result_P(result_string,test_group,data,del_total):
	resultpath = "./ResultP"+ '/' + result_string + '/' + test_db_name + '/d' + str(del_total) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'a')
	for d in data:
		filename.writelines(d)
	filename.close()


def write_result_G(result_string,test_group,data,del_total):
	resultpath = "./ResultG"+ '/' + result_string + '/' + test_db_name + '/d' + str(del_total) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'a')
	for d in data:
		filename.writelines(d)
	filename.close()


def write_search_time_G(test_group, Search_time, total_time, result_len,Client_bytes_len,Server_bytes_len,del_total):
	resultpath = "./ResultG"+ '/' + "DDSE2Srch" + '/' + test_db_name + '/d' + str(del_total) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'w')
	for ke in Search_time:
		filename.writelines('keyword:\t'+str(ke) +'\t'+ str(Search_time[ke])+ '\t' + str(total_time[ke])+'\t'+ str(result_len[ke])+ '\t'+ str(Client_bytes_len[ke]) + '\t' + str(Server_bytes_len[ke]) +'\n')
	filename.close()


def write_search_time_P(test_group, Search_time, total_time, result_len,Client_bytes_len,Server_bytes_len,del_total):
	resultpath = "./ResultP"+ '/' + "DDSE2Srch" + '/' + test_db_name + '/d' + str(del_total) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'w')
	for ke in Search_time:
		filename.writelines('keyword:\t'+str(ke) +'\t'+ str(Search_time[ke])+ '\t' + str(total_time[ke])+'\t'+ str(result_len[ke])+ '\t'+ str(Client_bytes_len[ke]) + '\t' + str(Server_bytes_len[ke]) +'\n')
	filename.close()

def bytes_to_base64(b):
	return base64.b64encode(b).decode('utf-8')

def ConvertRettoBlob(data):
	converted_data = (bytes_to_base64(data[0]), [bytes_to_base64(item) for item in data[1]])
	return json.dumps(converted_data)

def base64_to_bytes(s):
    return base64.b64decode(s.encode('utf-8'))


def ConvertBlobtoRet(json_data):
	loaded_data = json.loads(json_data)
	return (base64_to_bytes(loaded_data[0]), [base64_to_bytes(item) for item in loaded_data[1]])

def Test():
	l = list(test_phase)
	print ('*********************************************')
	print ('start test_group', test_group)
	print('start initial db')
	DB_Setup(test_db_name,data_scale,falut_to)
	Ciphertext_Gen_Phase()
	# pdb.set_trace()
	deletion_phase_with_search(del_num,del_rate)


if __name__ == "__main__":

		test_db_name = str(sys.argv[1])
		test_phase = str(sys.argv[2])
		test_group = str(sys.argv[3])
		del_num = int(sys.argv[4])
		del_rate = int(sys.argv[5])
		process_dec_num = int(sys.argv[6])
		data_scale = int(sys.argv[7])
		falut_to = float(sys.argv[8])
		Test()

