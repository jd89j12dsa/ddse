import hashlib
import json
import os
import base64
import pymongo
import math


class Util(object):
	"""docstring for Util"""
	def __init__(self):
		self.AES_BLOCK_SIZE = 16
		self.INT_size = 4

	def hash_to_32_bytes(self,input_string):
		md5_hash = hashlib.md5()
		input_bytes = input_string.encode('utf-8')
		md5_hash.update(input_bytes)
		return md5_hash.hexdigest()


	def bytes_to_base64(self,b):
		return base64.b64encode(b).decode('utf-8')
	
	def ConvertRettoBlob(self,data):
		converted_data = (self.bytes_to_base64(data[0]), [self.bytes_to_base64(item) for item in data[1]])
		return json.dumps(converted_data)
	
	def base64_to_bytes(self,s):
	    return base64.b64decode(s.encode('utf-8'))
	
	
	def ConvertBlobtoRet(self,json_data):
		loaded_data = json.loads(json_data)
		return (self.base64_to_bytes(loaded_data[0]), [self.base64_to_bytes(item) for item in loaded_data[1]])

	
	def write_table_result(self,resultpath,resultfilename,tablehead,table):
		if os.path.exists(resultpath) == False:
			os.makedirs(resultpath)
		
		filename = open(resultpath + resultfilename, 'w')
		head_str = '\t'.join(map(str,tablehead))
		filename.write(head_str+'\n')

		trans_table = zip(*table)

		for row in trans_table:
			row_str = '\t'.join(map(str,row))
			filename.write(row_str+'\n')

		filename.close()


	def read_scale(self,test_db_name):

		myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
		plaintextdb = myclient[test_db_name] 
		plaintext_col = plaintextdb["id_keywords"]
		plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)
		
		result = sum([ len(x['val_set']) for x in plaintext_cur])

		return result


	def read_dis_scale(self,test_db_name):

		myclient = pymongo.MongoClient("mongodb://localhost:27017/?maxPoolSize=600&w=0")
		plaintextdb = myclient[test_db_name] 
		plaintext_col = plaintextdb["id_keywords"]
		plaintext_cur = plaintext_col.find(no_cursor_timeout=True).batch_size(1000)
		
		result = sum([ len(list(set(x['val_set']))) for x in plaintext_cur])

		return result


	def estimateBFsize (self,n,p):
	
		bitSize=int(-n*math.log(p)/math.pow(math.log(2),2))
		hashFuncSize=int(bitSize*math.log(2)/n)
		return bitSize,hashFuncSize


	def getupdatesize(self,newbfbits,newkey,newinternal):
		# eliminate the inconsistent of Python memory allocation
		return newbfbits/8+newkey*self.AES_BLOCK_SIZE+newinternal*self.INT_size




		