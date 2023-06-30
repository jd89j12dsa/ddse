import pymongo
import time
import sys
import json
import random
import threading
import math
import os
from sys import getsizeof as getsize

import Diana
import DDSE3
import pymysql
import pdb

from pathos.multiprocessing import ProcessingPool
from collections import defaultdict
from BloomFilter import BloomFilter

import hashlib
import sys, os
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(1, os.path.abspath('..'))

from fhipe import ipe

UpCnt = defaultdict(lambda: 0 )
EDB_cache = dict()
mbf = dict()
tbf = dict()
vbf = dict()
random_set = [random.randint(0, 2**32) for i in range(20)]
Keywords_Cipher_Collection = dict()


def convert_to_vector(binary_bytes):
    
	result = [int.from_bytes(binary_bytes[i:i+4], byteorder='big') for i in range(0, len(binary_bytes), 4)]

	return result


def create_mysql_table():
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII')
	cursor = connection.cursor()
	sql = " DROP DATABASE IF EXISTS DDSE3"+str(test_db_name)+";"
	cursor.execute(sql)
	sql = " CREATE DATABASE DDSE3"+str(test_db_name)+" CHARACTER SET 'ASCII';"
	cursor.execute(sql)
	connection.close()
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII', database = 'DDSE3'+str(test_db_name))
	cursor = connection.cursor()
	sql = """
	CREATE TABLE `cipher`(
	`_id` int NOT NULL AUTO_INCREMENT,
	`tstamp` DOUBLE NOT NULL,
	`att_keyword` BLOB NOT NULL,
	`ipe` BLOB NOT NULL,
	`att_val` BLOB NOT NULL,
	PRIMARY KEY (`_id`),
	UNIQUE INDEX(`att_keyword`(32))
	) ENGINE = InnoDB DEFAULT CHARSET=ASCII;
	"""
	cursor.execute(sql)
	connection.close()	

def DB_Setup(test_db_name):
	global myclient,plaintextdb,ownerkey,Kh,Kt,Kc,mbf,pp,sk
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	plaintextdb = myclient[test_db_name] 
	dur, ownerkey, keyleft, keyright = Diana.Setup()
	dur, Kh, Kt, Kc = DDSE3.Setup()

	pp, sk = ipe.setup(10) 
	create_mysql_table()

def Encrypt(keyword,value_set,operation):
	global mbf,pp,sk,Kh,falut_to,UpCnt
	Keywords_Cipher = []
	encrypted_time = 0
	mbf[keyword] = BloomFilter(len(set(value_set)),falut_to)

	t_s = time.time()
	for value in value_set:
		#time_s = time.time()

		dur, t = DDSE3.PRF(Kt, keyword+str(value)+operation)

		mbf[keyword].add_tag(t)

		dur, bs = DDSE3.PRF(Kh, mbf[keyword].convert_to_string())

		ctx = ipe.encrypt(sk, convert_to_vector(bs)+[random_set[random.randint(0, len(random_set)-1)],0])
		
		dur, Evalue = DDSE3.AESEncrypt(Kc, operation+str(value))

		dur, ct = Diana.Encrypt(keyword , UpCnt[keyword])

		Keywords_Cipher.append((ct,time.time(),ctx,Evalue))

		UpCnt[keyword]+=1

	return time.time()-t_s, Keywords_Cipher

def write_cipher_to_db(data):
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII', database = 'DDSE3'+str(test_db_name))
	cursor = connection.cursor()

	try:
		sql = "INSERT INTO cipher (att_keyword, tstamp, ipe, att_val) VALUES (%s,%s,%s,%s)"
		cursor.executemany(sql,data)
		connection.commit()

	except Exception as e:

		print("ERROR OCC",e)

	finally:
		cursor.close()
		connection.close()


def process_Enc(plaintext_colpp,start,end):

	print(start,"start_calc","digiest:")
	#print(plaintext_colpp[0])

	upload_list = []
	tp = []

	t_s = time.time()

	for i in range(end):

		_, Keywords_Cipher = Encrypt(plaintext_colpp[i][0],plaintext_colpp[i][1],plaintext_colpp[i][2])
		upload_list.extend(Keywords_Cipher)

	print(start,'calc_comple',time.time()-t_s)

	return [time.time()-t_s,UpCnt,mbf,upload_list]


def Ciphertext_Gen_Phase():
	global plaintextdb,ciphercol,UpCnt,mbf

	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)

	total_encrypt_time = 0
	entry_counter = 0
	sector = 100000
	result = []
	upload_list = []
	p = []

	if process_num == 0:

		for plaintext in plaintext_cur:
			encrypted_time , Keywords_Cipher = Encrypt(plaintext['k'],plaintext['val_set'],'ins')
			# pdb.set_trace()
			entry_counter += len(Keywords_Cipher)
			total_encrypt_time += encrypted_time
			if entry_counter >= sector:
				sector += 100000
				result.append('len:\t'+str(entry_counter) +'\t'+ str(total_encrypt_time)+'\n')
				if len(result) > 100:
					print('wirtedata')
					write_result("DDSE3Add",test_group,result,0)
					result = []
			upload_list.extend(Keywords_Cipher)
			if len(upload_list)>= 200000:
				print("start slice")
				t=threading.Thread(target=write_cipher_to_db,args=(upload_list[:]))
				p.append(t)
				t.start()
				upload_list = []
	
		for t in p:
			t.join()
	
		if len(upload_list)> 0:
			write_cipher_to_db(upload_list)
			upload_list = []
		
		result.append('len:\t'+str(entry_counter) +'\t'+ str(total_encrypt_time)+'\n')
		if len(result) > 0:
			write_result("DDSE3Add",test_group,result,0)

	else:

		pool = ProcessingPool(process_num)
		plaintext_colpp = []
		cnt = 0

		tasklen = math.ceil(plaintext_cur.count()/process_num) 
		#pdb.set_trace()

		for plaintext in plaintext_cur:

			#pdb.set_trace()
			plaintext_colpp.append([plaintext['k'],plaintext['val_set'],'ins'])
			cnt += 1
			if cnt % tasklen == 0:
				p.append(pool.apipe(process_Enc,plaintext_colpp[:],cnt-tasklen,tasklen))
				plaintext_colpp	= []		

		if cnt% tasklen >0:
			p.append(pool.apipe(process_Enc,plaintext_colpp,cnt-(cnt% tasklen),cnt% tasklen))

		p = [e.get() for e in p]

		PUC = []

		for res in p:
			result_time, UpCntd, mbfd, Uc = res
			result.append(str(result_time)+'\n')
			for i in UpCntd:
				UpCnt[i] = UpCntd[i]
			for i in mbfd:
				mbf[i] = mbfd[i]
			PUC.extend(Uc)
		
		write_cipher_to_db(PUC)

		write_result("DDSE3Add"+str(process_num)+"P",test_group,result,0)

	return 

def write_result(result_string,test_group,data,del_total):
	resultpath = "./Result"+ '/' + result_string + '/' + test_db_name + '/d' + str(del_total) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'a')
	for d in data:
		filename.writelines(d)
	filename.close()

def deletion_phase_with_search(l_del_num,l_del_rate):
	global plaintextdb,ciphercol
	
	plaintext_col = plaintextdb["id_keywords_del_list"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)

	total_encrypt_time = 0
	entry_counter = 0
	sector = 100000
	result = []
	upload_list = []
	i = 0
	j = 0
	p = []

	if l_del_num == 0:

		Search_Phase(l_del_num,j)

	else:
		
		for plaintext in plaintext_cur:
			if i%l_del_num == 0:
	
				if len(upload_list)> 0:
					for t in p:
						t.join()
					p = []
					write_cipher_to_db(upload_list)
					upload_list = []
	
				result.append('len:\t'+str(entry_counter) +'\t'+ str(total_encrypt_time)+'\n')
				if len(result) > 0:
	
					if process_num == 0:
						write_result("DDSE3Del",test_group,result,l_del_num*j)
	
					else:
						write_result("DDSE3Del"+str(process_num)+"P",test_group,result,l_del_num*j)
	
				#pdb.set_trace()
				Search_Phase(l_del_num,j)
	
				j+=1
	
				#pdb.set_trace()
	
				if j == l_del_rate:
					break
			else:
				encrypted_time , Keywords_Cipher = Encrypt(plaintext['k'],plaintext['val_set'],'del')
				entry_counter += len(Keywords_Cipher)
				total_encrypt_time += encrypted_time
				if entry_counter >= sector:
					sector += 100000
					result.append('len:\t'+str(entry_counter) +'\t'+ str(total_encrypt_time)+'\n')
		
				upload_list.extend(Keywords_Cipher)
	
				if len(upload_list)>= 200000:
					print("start slice")
					t=threading.Thread(target=write_cipher_to_db,args=(upload_list[:]))
					p.append(t)
					t.start()
					upload_list = []
				i+=1


class MyThread(threading.Thread):
	def __init__(self, func, args=()):
		super(MyThread, self).__init__()
		self.func =func
		self.args = args
	def run(self):
		self.result = self.func(*self.args)

	def get_result(self):
		threading.Thread.join(self)
		try:
			return self.result
		except Exception:
			return None

def thread_find(clause):
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII', database = 'DDSE3'+str(test_db_name))
	cursor = connection.cursor()
	stri = ",".join(["%s"] * len(clause))
	sql = "SELECT tstamp,ipe,att_val FROM cipher WHERE att_keyword in ( "+stri+")"

	# pdb.set_trace()

	try:
		length = cursor.execute(sql,clause)
		connection.commit()

	except Exception as e:

		print("ERROR OCC",e)
		connection.rollback()

	re = cursor.fetchall()
	#print(re)
	re = [ [re[i][0],re[i][1],re[i][2]] for i in range(len(re))]
	cursor.close()
	connection.close()
	return re

def complex_thread_find(clause_list):
	result = []

	# pdb.set_trace()
	p =[MyThread(thread_find,(clause_list[i],)) for i in range(len(clause_list))]
	for t in p:
		t.start()
	for t in p:
		t.join()
	for t in p:
		result.extend(t.get_result())
	return result


def dec_ipe(sky,result):
	
	global pp

	dup_dict = dict()
	presult = []

	for i in result:
		if i[1] in dup_dict:
			presult.append(dup_dict[i[1]])
		else:
			dec = i[0],ipe.decrypt(pp,sky,i[1]),i[2]
			dup_dict[i[1]] = dec
			presult.append(dec)
	
	return presult


def complex_process_decode_ipe(sky,pp,result):
	pool = ProcessingPool(process_num)
	p = []

	#pdb.set_trace()

	cnt = 0
	tasklen = math.ceil(len(result)/process_num) 

	#print(len(result))
	for i in range(len(result)):
		cnt += 1
		if cnt % tasklen == 0:
			#pdb.set_trace()
			p.append(pool.apipe(dec_ipe,sky,result[cnt-tasklen:cnt]))

	if cnt% tasklen >0:
		p.append(pool.apipe(dec_ipe,sky,result[cnt-(cnt%tasklen) : cnt]))
	
	p = [e.get() for e in p]

	resize = []
	for li in p:
		resize.extend(li)


	sorted_all_task = sorted(resize, key = lambda x: x[0])
	
	#pdb.set_trace()

	unique_list = []
	seen = dict()
	for sublist in sorted_all_task:
		if sublist[1] not in seen:
			unique_list.append(sublist[2])
			seen[sublist[1]] = 1

	return unique_list


def process_decode_ipe(sky,pp,result):


	all_task = [ [result[i][0], ipe.decrypt(pp, sky, result[i][1]), result[i][2]] for i in range(len(result))]


	#sorted_all_task = sorted(all_task, key = lambda x: x[0])
	
	sorted_all_task = all_task

	# pdb.set_trace()

	unique_list = []
	seen = set()
	for sublist in sorted_all_task:
		if sublist[1] not in seen:
			unique_list.append(sublist[2])
			seen.add(sublist[1])

	return unique_list

def Search(keyword):
	global UpCnt,pp,sk,mbf
	#the client
	time_s = time.time()
	if keyword not in UpCnt:
		return 0, ""
	Conter = UpCnt[keyword]
	dur, k2, kc, kdepth = Diana.Trapdoor(keyword, Conter)
	dur, bs = DDSE3.PRF(Kh, mbf[keyword].convert_to_string())

	sky = ipe.keygen(sk, convert_to_vector(bs)+[0,random.randint(0,2**32)])

	# the server 
	minor_counter = 0
	clause_list = []
	clause = []
	for i in range(Conter):
		dur, ctcheck = Diana.Search( i, k2, kc, kdepth)
		clause.append(ctcheck)
		minor_counter+=1
		if minor_counter == 1000:
			clause_list.append(clause)
			minor_counter = 0
			clause = []
	if minor_counter > 0:
		clause_list.append(clause)
		clause = []

	time_e = time.time()
	time_user = time_e-time_s

	# server
	time_s = time.time()

	# pdb.set_trace()
	result = complex_thread_find(clause_list)

	# result = thread_find(clause)

	time_e = time.time()

	Re_lantency = time_e-time_s

	#print(Re_lantency)

	time_s = time.time()	

	output = []

	if process_num == 0:

		output = process_decode_ipe(sky,pp,result)

	else:
		output = complex_process_decode_ipe(sky,pp,result)

	time_server = time.time()-time_s + Re_lantency

	Server_bytes = sum(getsize(i) for i in output)

	output = [DDSE3.AESDecrypt(Kc,output[i]) for i in range(len(output))]

	#pdb.set_trace()
	# print(output)


	

	#if keyword not in EDB_cache:
	Client_bytes = getsize(k2)+getsize(kc)
	
	return time_server,time_user, Re_lantency, output, Client_bytes, Server_bytes


def Search_Phase(l_del_num,l_del_rate):
	global ownerkey,plaintextdb
	search_result = []
	Search_time = dict()
	result_len = dict()
	total_time = dict()
	Latency = dict()
	Client_bytes_len = dict()
	Server_bytes_len = dict()
	Search_Phase_time = 0

	cnt=0

	if l_del_rate == 0:
		search_col = plaintextdb["id_keyword_search_list"]
		plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
		task_search = [x["k"] for x in plaintext_cur]
		

	else:
		search_col = plaintextdb["id_keyword_search_list_del"]
		plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
		task_search = [x["k"] for x in plaintext_cur]

	for keyword in task_search:
		#pdb.set_trace()
		time_server,time_user, Re_lantency, S, Client_bytes, Server_bytes = Search(keyword)
		result_len[keyword] = len(S)
		Search_time[keyword] = time_server
		total_time [keyword] = time_server+time_user
		Latency[keyword] = Re_lantency
		Client_bytes_len[keyword] = Client_bytes
		Server_bytes_len[keyword] = Server_bytes
		cnt+= 1 
		if cnt % 200 == 0:
			print(l_del_num*l_del_rate,cnt,"process")
	print(l_del_num*l_del_rate,"success")
	write_search_time(test_group,Search_time,total_time,Latency, result_len,Client_bytes_len,Server_bytes_len,l_del_num*l_del_rate)

def write_search_time(test_group, Search_time, total_time,Latency, result_len,Client_bytes_len,Server_bytes_len,del_total):
	
	resultpath = "./Result"+ '/' + "DDSE3Srch" + '/' + test_db_name + '/d' + str(del_total) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	
	filename = open( resultpath + str(test_group),'w')

	for ke in Search_time:
		filename.writelines('keyword:\t'+str(ke) +'\t'+ str(Search_time[ke])+ '\t' + str(total_time[ke])+ '\t' + str(Latency[ke]) + '\t'+ str(result_len[ke])+ '\t'+ str(Client_bytes_len[ke]) + '\t' + str(Server_bytes_len[ke]) +'\n')
	filename.close()


def Test():
	l = list(test_phase)
	print ('*********************************************')
	print ('start test_group', test_group)

	print('start initial db')
	DB_Setup(test_db_name)
	Ciphertext_Gen_Phase()
	deletion_phase_with_search(del_num,del_rate)

if __name__ == "__main__":

		test_db_name = str(sys.argv[1])
		test_phase = str(sys.argv[2])
		test_group = str(sys.argv[3])
		del_num = int(sys.argv[4])
		del_rate = 6
		process_num = int(sys.argv[5])
		falut_to = float(sys.argv[6])

		fileids =[]
		keywords_set = []
		Test()

		