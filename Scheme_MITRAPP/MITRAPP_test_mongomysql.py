import Diana
import MITRAPP
import pymongo
import time
import pdb
import sys
import os
from sys import getsizeof
import threading
import pymysql
from pymongo import InsertOne

from collections import defaultdict

keyword_counter = dict()

def get_size(a):
	all_cap = 0
	for item in a:
		all_cap += sys.getsizeof(item)
	return all_cap

def create_mysql_table ():
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII')
	cursor = connection.cursor()
	sql = " DROP DATABASE IF EXISTS DDSE1"+str(test_db_name)+";"
	cursor.execute(sql)
	sql = " CREATE DATABASE DDSE1"+str(test_db_name)+" CHARACTER SET 'ASCII';"
	cursor.execute(sql)
	connection.close()
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII', database = 'DDSE1'+str(test_db_name))
	cursor = connection.cursor()
	sql = """
	CREATE TABLE `cipher`(
	`_id` int NOT NULL AUTO_INCREMENT,
	`att_keyword` BLOB NOT NULL,
	`att_val` BLOB NOT NULL,
	PRIMARY KEY (`_id`),
	INDEX(`att_keyword`(100))
	) ENGINE = InnoDB DEFAULT CHARSET=ASCII;
	"""
	cursor.execute(sql)
	connection.close()	
def DB_Setup(test_db_name):
	global myclient,mydb,plaintextdb,ownerkey,connection
	myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
	mydb = myclient["MITRAPP"+test_db_name]
	plaintextdb = myclient[test_db_name]
	dur, ownerkey, keyleft, keyright = Diana.Setup()
	create_mysql_table()

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
		dur, ct1=Diana.Encrypt(keyword , keyword_counter[keyword])
		ct2 = retrievecipher
		keyword_counter[keyword] +=1
		time_e = time.time()
		encrypted_time += (time_e - time_s)
		Keywords_Cipher.append((ct1,ct2))

	return encrypted_time, Keywords_Cipher

def write_cipher_to_db(data):
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII', database = 'DDSE1'+str(test_db_name))
	cursor = connection.cursor()
	sql = "INSERT INTO cipher (att_keyword,att_val) VALUES (%s,%s)"
	cursor.executemany(sql,data)
	connection.commit()
	cursor.close()
	connection.close()

def Ciphertext_Gen_Phase():
	global plaintextdb,ciphercol,mydb
	plaintext_col = plaintextdb["id_keywords"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)
	sector = 1000
	total_encrypt_time = 0
	entry_counter = 0
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
				print('wirtedata')
				write_result("MitrappAdd",test_group,result)
				result = []
		upload_list.extend(Keywords_Cipher)
		if len(upload_list)>= 200000:
			t=threading.Thread(target=write_cipher_to_db,args=(upload_list[:],))
			t.start()
			upload_list = []

	if len(upload_list)> 0:
		t=threading.Thread(target=write_cipher_to_db,args=(upload_list[:],))
		t.start()
		upload_list = []
	if len(result) > 0:
		write_result("MitrappAdd",test_group,result)	

	return

def deletion_phase(del_num):
	global plaintextdb,mydb,ciphercol
	plaintext_col = plaintextdb["id_keywords_del_list"]
	plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)
	total_encrypt_time = 0
	entry_counter = 0
	sector = 1000
	result = []
	upload_list = []
	cnt = 0
	for plaintext in plaintext_cur:
		if cnt == del_num:
			break
		encrypted_time , Keywords_Cipher = Encrypt(plaintext['k'],plaintext['val_set'],'del')
		entry_counter += len(Keywords_Cipher)
		total_encrypt_time += encrypted_time
		if entry_counter >= sector:
			sector += 1000
			result.append('len:\t'+str(entry_counter) +'\t'+ str(total_encrypt_time)+'\n')
			if len(result) > 100:
				print('wirtedata')
				write_result("MitrappDel",test_group,result)
				result = []
		upload_list.extend(Keywords_Cipher)
		if len(upload_list)>= 200000:
			t=threading.Thread(target=write_cipher_to_db,args=(upload_list[:],))
			t.start()
			upload_list = []
		cnt+=1

	if len(upload_list)> 0:
		t=threading.Thread(target=write_cipher_to_db,args=(upload_list[:],))
		t.start()
		upload_list = []
	if len(result) > 0:
		write_result("MitrappDel",test_group,result)	

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
	connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII', database = 'DDSE1'+str(test_db_name))
	cursor = connection.cursor()
	stri = ",".join(["%s"] * len(clause))
	sql = "SELECT att_val FROM cipher WHERE att_keyword in ( "+stri+")"
	cnt = 0

	while 1:
		lenth = cursor.execute(sql,clause)
		connection.commit()
		if lenth>0:
			break
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

def Search(keyword):
	global keyword_counter
	result = []
	if keyword not in keyword_counter:
		return 0, ""
	Conter = keyword_counter[keyword]
	dur, k2, kc, kdepth = Diana.Trapdoor(keyword, Conter)
	minor_counter = 0
	clause_list = []
	clause = []
	time_s = time.time()
	for i in range(Conter):
		dur, ctcheck = Diana.Search( i, k2, kc, kdepth)
		clause.append(ctcheck)
		minor_counter+=1
		if minor_counter == 50:
			clause_list.append(clause)
			minor_counter = 0
			clause = []
	if minor_counter > 0:
		clause_list.append(clause)
		clause = []
	result = complex_thread_find(clause_list)
	time_e = time.time()
	return time_e-time_s, result
def Search_Phase():
	global mydb,keyword_counter,ownerkey,plaintextdb
	time.sleep(50)  # wait for writing log file
	Search_time = dict()
	latency = dict()
	match_len = dict()
	result_len = dict()
	Search_Phase_time = 0
	search_col = plaintextdb["id_keyword_search_list"]
	plaintext_cur = search_col.find(no_cursor_timeout=True).batch_size(1000)
	task_search = [x["k"] for x in plaintext_cur]
	#pdb.set_trace()
	for keyword in task_search:
		if keyword == 'F0':
			dur,re = Search(keyword)
		time_s = time.time()
		DupM = defaultdict(lambda: 0)
		dur,re = Search(keyword)
		#pdb.set_trace()
		latency[keyword] = dur
		search_result = []
		dur,session = MITRAPP.PRF(ownerkey,keyword)
		for y in re:
			dur, x = MITRAPP.AESDecrypt(session,y)
			#pdb.set_trace()
			x = x.replace("%","")
			p = x.split("$")[0]
			if x[-3:] == 'ins' :
				search_result.append(p)
				search_result = list(set(search_result))
			if x[-3:] == 'del' :
				search_result.remove(p)
		time_e = time.time()
		#print(search_result)
		result_len[keyword] = len(search_result)
		match_len[keyword] = sum([sys.getsizeof(rei) for rei in re]) 
		Search_time[keyword] = time_e-time_s
	write_search_time(test_group,latency,Search_time, match_len,result_len)


def write_search_time(test_group, latency, Search_time,match_len,result_len):

	resultpath = "./Result"+ '/' + "MITRAPPSrch" + '/' + test_db_name + '/d' + str(del_num) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'w')
	for ke in Search_time:
		filename.writelines('keyword:\t'+str(ke) +'\t'+ str(latency[ke]) + '\t' + str(Search_time[ke])+ '\t' + str(match_len[ke])+'\t'+ str(result_len[ke])+ '\n')
	filename.close()



def write_result(result_string,test_group,data):
	resultpath = "./Result"+ '/' + result_string + '/' + test_db_name + '/d' + str(del_num) + '/'
	if os.path.exists(resultpath) == False:
		os.makedirs(resultpath)	

	filename = open( resultpath + str(test_group),'a')
	for d in data:
		filename.writelines(d)
	filename.close()


def Test():
	l = list(test_phase)
	print ('*********************************************')
	print ('test_on ', test_db_name, 'del_num ', del_num)
	print ('start test_group ', test_group)

	if 'b' in l:
		print('start initial db')
		DB_Setup(test_db_name)
	else:
		DB_Connect(test_db_name)
	if 'c' in l:
		Ciphertext_Gen_Phase()
	if 'd' in l:
		deletion_phase(del_num)
	if 's' in l:
		print('start search')
		Search_Phase()

if __name__ == "__main__":

		test_db_name = str(sys.argv[1])
		test_phase = str(sys.argv[2])
		test_group = str(sys.argv[3])
		del_num = int(sys.argv[4])
		fileids =[]
		keywords_set = []
		Test()

	