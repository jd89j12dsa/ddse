import pymysql
from MyThread import MyThread

class MysqlOP():

	def __init__(self, test_db_name:str, max_connection_size:int):
		connection = pymysql.connect(host='localhost',user='root', password='root', charset='utf8')
		cursor = connection.cursor()
		sql = " DROP DATABASE IF EXISTS ddse2"+str(test_db_name)+";"
		cursor.execute(sql)
		sql = " CREATE DATABASE ddse2"+str(test_db_name)+" CHARACTER SET 'utf8';"
		cursor.execute(sql)
		connection.commit()
		connection.close()
		connection = pymysql.connect(host='localhost',user='root', password='root', charset='utf8', database = 'ddse2'+str(test_db_name))
		cursor = connection.cursor()
		sql = """
		CREATE TABLE `cipher`(
		`_id` int NOT NULL AUTO_INCREMENT,
		`att_keyword` BLOB NOT NULL,
		`att_val` BLOB NOT NULL,
		PRIMARY KEY (`_id`),
		INDEX(`att_keyword`(32))
		) ENGINE = InnoDB DEFAULT CHARSET=utf8;
		"""
		cursor.execute(sql)
		connection.close()	

		self.db_config = {
		'host' : 'localhost',
		'user' : 'root',
		'password' : 'root',
		'db': 'ddse2'+str(test_db_name)
		}
		self.max_connection_size = max_connection_size

	def write_cipher_to_db(self,data):

		try:
			connection = pymysql.connect(**self.db_config)
	
			with connection.cursor() as cursor:
				sql = "INSERT INTO cipher (att_keyword,att_val) VALUES (%s,%s)"
				cursor.executemany(sql,data)
	
			connection.commit()

		except Exception as e:
			print(f"An error occurred: {str(e)}")

		finally:
			connection.close()

	def thread_find(self,clause):
		re = []
		try:

			connection = pymysql.connect(**self.db_config)

			with connection.cursor() as cursor:
				stri = ",".join(["%s"] * len(clause))
				sql = "SELECT att_val FROM cipher WHERE att_keyword in ( "+stri+")"
				cursor.execute(sql,clause)
				re = cursor.fetchall()

			connection.commit()

		except Exception as e:
			print(f"An error occurred: {str(e)}")

		finally:

			connection.close()
	
		re = [re[i][0] for i in range(len(re))]
		return re
	
	def complex_thread_find(self,clause_input):
		result = []

		chunk_size = len(clause_input)//self.max_connection_size
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

