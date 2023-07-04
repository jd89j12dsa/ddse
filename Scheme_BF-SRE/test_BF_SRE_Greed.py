import pymongo
import time
import os
import sys
import json
import threading
from sys import getsizeof as getsize
from SRE_Boost import SRE
import Diana
import DDSE2
import pymysql
import pdb
from pymongo import InsertOne
from collections import defaultdict
from BloomFilter import BloomFilter

UpCnt = defaultdict(lambda: 0 )
EDB_cache = dict()
Keywords_Cipher_Collection = dict()

def create_mysql_table():
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='utf8')
	cursor = connection.cursor()
	sql = " DROP DATABASE IF EXISTS ddse2"+str(test_db_name)+";"
	cursor.execute(sql)
	sql = " CREATE DATABASE ddse2"+str(test_db_name)+" CHARACTER SET 'utf8';"
	cursor.execute(sql)
	connection.close()
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='utf8', database = 'ddse2'+str(test_db_name))
	cursor = connection.cursor()
	sql = """
	CREATE TABLE `cipher`(
	`_id` int NOT NULL AUTO_INCREMENT,
	`att_keyword` BLOB NOT NULL,
	`att_val` BLOB NOT NULL,
	PRIMARY KEY (`_id`),
	INDEX(`att_keyword`(100))
	) ENGINE = InnoDB DEFAULT CHARSET=utf8;
	"""
	cursor.execute(sql)
	connection.close()	

def DB_Setup(test_db_name,data_scale,falut_to):
	global myclient,mydb,datadb,task_search_list,internal,plaintextdb,ownerkey,sre,Ks,Kt,Kc,mbf
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	mydb = myclient["DDSE2"+test_db_name]
	plaintextdb = myclient[test_db_name] 
	dur, ownerkey, keyleft, keyright = Diana.Setup()
	dur, Ks, Kt, Kc = DDSE2.Setup()
	sre = SRE()
	mbf = BloomFilter(n=data_scale,p=falut_to)
	create_mysql_table()

def Encrypt(keyword,value_set,operation):
	global sre,mbf
	retrieve = ()
	ct = b''
	Keywords_Cipher = []
	encrypted_time = 0
	if operation == 'ins':
		blen = len(value_set)
		sre.init_keywordbf(keyword,blen,falut_to)
	for value in value_set:
		valuein = hash(value)
		if valuein < 0:
			valuein += sys.maxsize + 1
		time_s = time.time()
		dur, t = DDSE2.PRF(Kt, keyword+str(valuein))
		dur, u = DDSE2.PRF(Kc, str(UpCnt[keyword]))
		if operation == 'ins':
			if mbf.contains(t) == False:
				mbf.add_tag(t)
				retrieve = sre.Enc(keyword,valuein,t)
				#pdb.set_trace()
				dur, ct = Diana.Encrypt(keyword , UpCnt[keyword])
			else:
				retrieve = sre.Enc(keyword, valuein, DDSE2.Xor(t,u))
				#pdb.set_trace()
				sre.Comp(keyword,DDSE2.Xor(t,u))
				dur, ct = Diana.Encrypt(keyword, UpCnt[keyword])
			retrieve = json.dumps(retrieve).encode('utf-8')
			Keywords_Cipher.append((ct,retrieve))
			UpCnt[keyword]+=1

		else:
			sre.Comp(keyword,t)

		#pdb.set_trace()
		sre.Comp(keyword,b'0')
		time_e = time.time()
		encrypted_time += (time_e - time_s)
	return encrypted_time, Keywords_Cipher

def write_cipher_to_db(data):
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='utf8', database = 'ddse2'+str(test_db_name))
	cursor = connection.cursor()
	sql = "INSERT INTO cipher (att_keyword,att_val) VALUES (%s,%s)"
	cursor.executemany(sql,data)
	connection.commit()
	cursor.close()
	connection.close()

def Ciphertext_Gen_Phase():
	global plaintextdb,ciphercol,mydb,sre

	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)

	total_encrypt_time = 0
	entry_counter = 0
	sector = 1000
	result = []
	upload_list = []
	for plaintext in plaintext_cur:
		encrypted_time , Keywords_Cipher = Encrypt(plaintext['k'],plaintext['val_set'],'ins')
		entry_counter += len(Keywords_Cipher)
		total_encrypt_time += encrypted_time
		if entry_counter >= sector:
			sector += 1000
			result.append('len:\t'+str(entry_counter) +'\t'+ str(total_encrypt_time)+'\n')
			if len(result) > 100:
				# print('wirtedata')
				# write_result("DDSE2Add",test_group,result,0)
				result = []
		upload_list.extend(Keywords_Cipher)
		if len(upload_list)>= 20000:
			# print("start slice")
			write_cipher_to_db(upload_list)
			upload_list = []

	print('Average Update time cost: ',total_encrypt_time/entry_counter)
	print('Wait to write into database')

	if len(upload_list)> 0:
		write_cipher_to_db(upload_list)
		"""
		for data in upload_list:
			Keywords_Cipher_Collection[hash(data[0])] = data[1]
		"""
		upload_list = []
	# if len(result) > 0:
		# write_result("DDSE2Add",test_group,result,0)	
	return

def write_result(result_string,test_group,data,del_total):
	resultpath = "./ResultG"+ '/' + result_string + '/' + test_db_name + '/d' + str(del_total) + '/'
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
				# if len(result) > 0:
	
					# if process_dec_num == 0:
					# 	write_result("DDSE2Del",test_group,result,l_del_num*j)
	
					# else:
					# 	write_result("DDSE2Del"+str(process_dec_num)+"P",test_group,result,l_del_num*j)
	
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
					# print("start slice")
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
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='utf8', database = 'ddse2'+str(test_db_name))
	cursor = connection.cursor()
	stri = ",".join(["%s"] * len(clause))
	sql = "SELECT att_val FROM cipher WHERE att_keyword in ( "+stri+")"
	cnt = 0

	try:
		length = cursor.execute(sql,clause)
		connection.commit()

	except Exception as e:

		# print("ERROR OCC",e)
		connection.rollback()

	re = cursor.fetchall()
	re = [re[i][0] for i in range(len(re))]
	cursor.close()
	connection.close()
	return re

def complex_thread_find(clause_list):
	global mydb
	result = []
	p =[MyThread(thread_find,(clause_list[i],)) for i in range(len(clause_list))]
	for t in p:
		t.start()
	for t in p:
		t.join()
	for t in p:
		result.extend(t.get_result())
	return result

def complex_thread_decode_dec(keyword,skR,result,process_dec_num):
		global sre
		dec_list = [json.loads(result[i].decode('utf-8')) for i in range(len(result))]
		cts = []
		for ct in dec_list:
			if sre.Dec_check(keyword,ct) == 0:
				cts.append(ct)

		output = sre.complex_process_dec(keyword,skR,cts,process_dec_num)
		return output

def Search(keyword):
	global UpCnt,sre
	#the client
	time_s = time.time()
	if keyword not in UpCnt:
		return 0, ""
	Conter = UpCnt[keyword]
	dur, k2, kc, kdepth = Diana.Trapdoor(keyword, Conter)
	sk , skR = sre.cKRev(keyword)
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
	time_s = time.time()
	#pdb.set_trace()
	#result = find_at_local(clause_list)
	result = complex_thread_find(clause_list)
	#pdb.set_trace()
	
	output = []
	#if process_dec_num == 0:
	for i in range(len(result)):
		ct = json.loads(result[i].decode('utf-8'))
		#ct = result[i]
		output.append(sre.Dec_line(keyword,skR, ct))
	#else :
	#	output = complex_thread_decode_dec(keyword,skR,result,process_dec_num)
	#print(output)
	time_e = time.time()
	sre.Resetdeckey()
	time_server = time_e-time_s
	#if keyword not in EDB_cache:
	Client_bytes = getsize(k2)+getsize(kc)+getsize(sk)+getsize(skR)+sre.getbloomfiltersize(keyword)
	Server_bytes = getoutputsize(output)
	return time_server,time_user, output, Client_bytes, Server_bytes

def getoutputsize(output):
	size = 0
	for i in output:
		if i is not None:
			size+= getsize(i)
	return size


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
		search_col = plaintextdb["id_keyword_search_list_del"]
		plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
		task_search = [x["k"] for x in plaintext_cur]

	task_search = task_search[0:1]

	for keyword in task_search:
		time_server,time_user, S, Client_bytes, Server_bytes = Search(keyword)
		#pdb.set_trace()
		
		result_len[keyword] = len(S)
		Search_time[keyword] = time_server
		total_time [keyword] = time_server+time_user
		Client_bytes_len[keyword] = Client_bytes
		Server_bytes_len[keyword] = Server_bytes

	print('Rep. Kword result-\t', "Search_time: ", str(Search_time[task_search[0]]), '\tComm. cost: ', str(Server_bytes_len[task_search[0]]/1024) + 'KB' + '\n') 
	# print(l_del_num*l_del_rate,"success")	
	# write_search_time(test_group,Search_time,total_time, result_len,Client_bytes_len,Server_bytes_len,l_del_num*l_del_rate)

def write_search_time(test_group, Search_time, total_time, result_len,Client_bytes_len,Server_bytes_len,del_total):
	resultpath = "./ResultG"+ '/' + "DDSE2Srch" + '/' + test_db_name + '/d' + str(del_total) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'w')
	for ke in Search_time:
		filename.writelines('keyword:\t'+str(ke) +'\t'+ str(Search_time[ke])+ '\t' + str(total_time[ke])+'\t'+ str(result_len[ke])+ '\t'+ str(Client_bytes_len[ke]) + '\t' + str(Server_bytes_len[ke]) +'\n')
	filename.close()


def Test():
	l = list(test_phase)
	print('-----------Test BF-SRE-G-----------')
	print('test_group: ', test_group, 'test_db_name: ', test_db_name, 'del_num: ', del_num, 'processors_num: ', process_dec_num, 'falut_tolrance: ', falut_to)
	print('start initial db')
	DB_Setup(test_db_name,data_scale,falut_to)
	Ciphertext_Gen_Phase()
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
		fileids =[]
		keywords_set = []
		Test()

		