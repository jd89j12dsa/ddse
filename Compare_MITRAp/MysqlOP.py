import pymysql
from MyThread import MyThread


class MysqlOP(object):
	"""docstring for MysqlOP"""
	def __init__(self, test_db_name:str, max_connection_size:int):
		connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII')
		cursor = connection.cursor()
		sql = " DROP DATABASE IF EXISTS DDSE1"+str(test_db_name)+";"
		cursor.execute(sql)
		sql = " CREATE DATABASE DDSE1"+str(test_db_name)+" CHARACTER SET 'utf8';"
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
		) ENGINE = InnoDB DEFAULT CHARSET=utf8;
		"""
		cursor.execute(sql)
		connection.close()
		connection = pymysql.connect(host='localhost',user='root', password='root', charset='ASCII', database = 'DDSE1'+str(test_db_name))
		cursor = connection.cursor()
		sql = """
		CREATE TABLE `cipher2`(
		`_id` int NOT NULL AUTO_INCREMENT,
		`att_keyword` BLOB NOT NULL,
		`att_val` BLOB NOT NULL,
		PRIMARY KEY (`_id`),
		INDEX(`att_keyword`(100))
		) ENGINE = InnoDB DEFAULT CHARSET=utf8;
		"""
		cursor.execute(sql)
		connection.close()	

		self.db_config = {
		'host' : 'localhost',
		'user' : 'root',
		'password' : 'root',
		'charset' : 'ASCII',
		'db': 'DDSE1'+str(test_db_name)
		}
		self.max_connection_size = max_connection_size


	def thread_find(self,clause):
		connection = pymysql.connect(**self.db_config)
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
		re = [ re[i][0] for i in range(len(re))]
		cursor.close()
		connection.close()
		return re
	
	def complex_thread_find(self,Conter,clause_input):
		result = []

		chunk_size = Conter//self.max_connection_size
		if chunk_size == 0:
			chunk_size = 2
		clause_list = [clause_input[i:i+chunk_size] for i in range(0,len(clause_input),chunk_size)]
		p =[MyThread(self.thread_find,(clause_list[i],)) for i in range(len(clause_list))]
		for t in p:
			t.start()
		for t in p:
			t.join()
		for t in p:
			result.extend(t.get_result())
		return result



	def write_cipher_to_db(self,data):

		connection = pymysql.connect(**self.db_config)
		cursor = connection.cursor()
		sql = "INSERT INTO cipher (att_keyword,att_val) VALUES (%s,%s)"
		cursor.executemany(sql,data)
		connection.commit()
		cursor.close()
		connection.close()
	
	def write_cipher_to_db_2(self,data):
		
		connection = pymysql.connect(**self.db_config)
		cursor = connection.cursor()
		sql = "INSERT INTO cipher2 (att_keyword,att_val) VALUES (%s,%s)"
		cursor.executemany(sql,data)
		connection.commit()
		cursor.close()
		connection.close()	
