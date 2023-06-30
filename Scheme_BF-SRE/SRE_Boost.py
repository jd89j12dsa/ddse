# -*- coding: utf-8 -*-
import ctypes
import math
import sys
import time
import pdb
import binascii
import threading
from sys import getsizeof as getsize
from BloomFilter import BloomFilter
from collections import defaultdict
import hashlib, hmac
from Crypto.Cipher import AES
from pathos.multiprocessing import ProcessingPool
from multiprocess import Pipe
import os

_xormap = {('0', '1'): '1', ('1', '0'): '1', ('1', '1'): '0', ('0', '0'): '0'}

class SRE:
	"""docstring for SRE"""
	def __init__(self, iv = b'0000000000000000',n = 200000,p = 0.0001, key_length=32): # 
		self.SK0 = os.urandom(key_length)
		self.SKI = os.urandom(key_length)
		self.fixed_iv = iv
		self.SKR={}
		self.bf = dict()
		self.deckey = defaultdict(lambda: 0)
		self.deckeyused = defaultdict(lambda: 0)

	def init_keywordbf (self, keyword, n, p):
		self.bf[keyword] = BloomFilter(n,p)

	def crypto_primitives_hmac(self, key,msg):
		hash_msg = hmac.new(key, msg, hashlib.sha256).digest()
		return hash_msg

	def getbloomfiltersize(self, keyword ):
		return getsize(self.bf[keyword])

	def padto33int (self, message):
		str_message = str(message)
		#pdb.set_trace()
		str_message = str_message + ''.join(['8' for i in range(0,33-len(str_message))])
		return int(str_message)

	def Enc(self,keyword,message,tag):
		iv = self.fixed_iv  # 16位字符串
		message = self.padto33int(message)
		tag=self.crypto_primitives_hmac(self.SK0, tag)
		t_id = self.string2HashedBinary(tag)  # binary of 8 digits
		sk = self.encrypt(self.keytrim(self.SK0), keyword, iv) # keyword->msk
		(index_list, hashmy)=self.bf[keyword].get_index_ij(t_id)
		ct_list=()
		ct_list_me=[]
		for i in range( self.bf[keyword].hashnum()):
			ij = index_list[i]
			ij = str(bin(ij)[2:]).zfill(int(math.log2(self.bf[keyword].bitSize)) + 1)
			k_id = 0
			result = sk
			for myi in range(len(ij)):
				result = self.encrypt(self.keytrim(result), ij[myi], iv)

			int_result = int.from_bytes(result, sys.byteorder)
			k_id = k_id ^ int_result
			encrypted_id = k_id ^ int(message)
			ct_list_me.append(encrypted_id)

		ct_list=tuple(item for item in ct_list_me)
		return [ct_list,t_id]

	def Calcsymkey(self,keyword,deletion_paths,sector,ends):
		iv = self.fixed_iv
		tagp = hash(str(deletion_paths))
		dict_i = dict()
		for i in range(sector,ends):
			ijs = str(bin(i)[2:]).zfill(int(math.log2(self.bf[keyword].bitSize)) + 1)
			k_id = 0
			# it searches for historical deleted path to identify F(sk)
			#pdb.set_trace()
			for del_path in deletion_paths:
				# print("del_path:", del_path)
				for del_item in del_path:
					if del_item[1] == ijs[0:len(del_item[1])]:
						if len(del_item[1]) != len(ijs): 
							result = del_item[0]
							for ips in range(len(del_item[1]), len(ijs)):
								result = self.encrypt(self.keytrim(result), ijs[ips], iv)
							k_id = k_id ^ int.from_bytes(result, sys.byteorder)
						else:
							k_id = k_id ^ int.from_bytes(del_item[0], sys.byteorder)
						break
			dict_i[i] = k_id
		return dict_i
		            
	def Deckeypool(self,keyword,deletion_paths):
		iv = self.fixed_iv
		b = self.bf[keyword].get_bitnum()
		BR = self.bf[keyword].get_bitarray()
		tagp = hash(str(deletion_paths))

		all_task = []
		pool = ProcessingPool(20)
		result = []
		sector = 0
		for i in range(b):
			if i % 200000 == 0 and i >0:
				#print(i)
				all_task.append(pool.apipe(self.Calcsymkey,keyword,deletion_paths,sector,i))
				sector = i
			if i == b-1 and b!= 200001:
				#print(i)
				all_task.append(pool.apipe(self.Calcsymkey,keyword,deletion_paths,sector,i))
		all_task = [e.get() for e in all_task]
		for res in all_task:
			for i in res:
				self.deckey[i] = res[i]

		return
					
	def Dec(self, keyword, deletion_paths, ct_list):
		cur_tag = ct_list[1]#tag
		if not self.bf[keyword].contains(cur_tag):
			iv = self.fixed_iv
			b = self.bf[keyword].get_bitnum()
			BR = self.bf[keyword].get_bitarray()
			tagp = hash(str(deletion_paths))
			for i in range(b):
				if BR[i] == 0:
					k_id = self.deckey[i]
					for eachentry in ct_list[0]:
						fileIdentifer = k_id ^ eachentry
						if len(str(fileIdentifer)) == 33:
							return (fileIdentifer, cur_tag)
		else:
			return (0,0)

	def Dec_line(self, keyword,deletion_paths, ct_list):
		cur_tag = ct_list[1]#tag
		if not self.bf[keyword].contains(cur_tag):
			iv = self.fixed_iv
			b = self.bf[keyword].get_bitnum()
			BR = self.bf[keyword].get_bitarray()
			#pdb.set_trace()
			deckey = self.deckey
			I = []
			for i in range(b):
				if i not in deckey:
					if BR[i] == 0:
						ijs = str(bin(i)[2:]).zfill(int(math.log2(self.bf[keyword].bitSize)) + 1)
						k_id = 0
						# it searches for historical deleted path to identify F(sk)
						for del_path in deletion_paths:
							# print("del_path:", del_path)
							for del_item in del_path:
								if del_item[1] == ijs[0:len(del_item[1])]:
									if len(del_item[1]) != len(ijs): 
										result = del_item[0]
										for i in range(len(del_item[1]), len(ijs)):
											result = self.encrypt(self.keytrim(result), ijs[i], iv)
										k_id = k_id ^ int.from_bytes(result, sys.byteorder)
									else:
										k_id = k_id ^ int.from_bytes(del_item[0], sys.byteorder)
									break
						deckey[i] = k_id
						for eachentry in ct_list[0]:
							fileIdentifer = k_id ^ eachentry
							if len(str(fileIdentifer)) == 33:
								return (fileIdentifer, cur_tag)
				else:
					k_id = deckey[i]
					for eachentry in ct_list[0]:
						fileIdentifer = k_id ^ eachentry
						if len(str(fileIdentifer)) == 33:
							return (fileIdentifer, cur_tag)
			return (0,0)

	def Resetdeckey(self):
		self.deckey = defaultdict(lambda: 0)
		self.deckeyused = defaultdict(lambda: 0)
		return

	def dec_pool(self,keyword,skR,dec_list):
		result =[]
		for i in range(len(dec_list)):
			result.append(self.Dec_line(keyword,skR,dec_list[i]))
		return result

	def complex_process_dec(self,keyword,skR,dec_list,process_dec_num):

		result = []
		all_task = []
		pool = ProcessingPool(process_dec_num)
		sector = 0
		slen = len(dec_list)// process_dec_num
		for i in range(len(dec_list)):
			if i == sector+slen and i!= len(dec_list)-1:
				all_task.append(pool.apipe(self.dec_pool,keyword,skR,dec_list[sector:slen]))
				sector += slen
			if i == len(dec_list)-1 :
				all_task.append(pool.apipe(self.dec_pool,keyword,skR,dec_list[sector:]))
		all_task = [e.get() for e in all_task]
		for res in all_task:
			result.extend(res)

		return result
	def Dec_check(self,keyword,ct_list):
			cur_tag = ct_list[1]
			if not self.bf[keyword].contains(cur_tag):
				return 0
			else :
				return 1

	def Comp(self,keyword, tag): # input the tag
		identifier_t =self.crypto_primitives_hmac(self.SK0, tag)
		t_id = self.string2HashedBinary(identifier_t)  # binary of 8 digits
		self.bf[keyword].add_tag(t_id)
		return 
	def cKRev(self,keyword): # keyword -> D[w]
		iv = self.fixed_iv  # 16位字符串
		b = self.bf[keyword].get_bitnum()
		enc_keyword = self.crypto_primitives_hmac(self.SK0,bytes(keyword, 'utf-8'))  # this is used to encrypt the keyword
		BR=self.bf[keyword].get_bitarray()
		I=[]
		for i in range(b):
			if BR[i] ==1:
				t_id1 = str(bin(i)[2:]).zfill(int(math.log2(self.bf[keyword].bitSize)) + 1)
				I.append(t_id1)
		sk = self.encrypt(self.keytrim(self.SK0), keyword, iv)
		path_tuples = []
		ff=0
		for t_id in I:
			if ff==0:
				ff=ff+1
				traveled_add = ''
				for b_index in range(len(t_id)):
					if len(traveled_add) == 0:
						if t_id[b_index] == '0':
							result = self.encrypt(self.keytrim(sk), '1', iv)
							i_tuple = (result, '1')
							path_tuples.append(i_tuple)
						else:
							result = self.encrypt(self.keytrim(sk), '0', iv)
							i_tuple = (result, '0')
							path_tuples.append(i_tuple)
					else:
						t_path = ''
						if t_id[b_index] == '0':
							t_path = traveled_add + '1'
						else:
							t_path = traveled_add + '0'
						result = sk
						for tranvers_digit in t_path:
							result = self.encrypt(self.keytrim(result), tranvers_digit, iv)
						i_tuple = (result, t_path)
						path_tuples.append(i_tuple)
					traveled_add += t_id[b_index]
	
			traveled_del = ''
			for del_item in path_tuples:
				if (del_item[1] == t_id[:len(del_item[1])]):
				# 将对应于tag_del的节点删除
					path_tuples.remove(del_item)
					if (len(del_item[1]) != len(t_id)):
						traveled_del = del_item[1]
						for b_index in range(len(del_item[1]), len(t_id)):
							t_path = ''
							if t_id[b_index] == '0':
								t_path = traveled_del + '1'
							else:
								t_path = traveled_del + '0'
							result = sk
							for tranvers_digit in t_path:
								result = self.encrypt(self.keytrim(result), tranvers_digit, iv)

						i_tuple = (result, t_path)
						path_tuples.append(i_tuple)
						traveled_del += t_id[b_index]
					break

		if enc_keyword not in self.SKR:
			self.SKR[enc_keyword] = [path_tuples]
		else:
			self.SKR[enc_keyword].append(path_tuples)
		return (sk,self.SKR[enc_keyword])		

	def encrypt(self, key, raw, iv):
		raw = self._pad(raw)
		cipher = AES.new(key,AES.MODE_CBC,iv)
       # cipher = AES.new(key.encode('utf8', AES.MODE_CBC, iv.encode('utf8'))
		return cipher.encrypt(raw.encode('utf-8'))

	def decrypt(self,key, ctext,iv):
		cipher = AES.new(key,AES.MODE_CBC,iv)
		return self._unpad(cipher.decrypt(ctext))

	def string2HashedBinary(self, msg):
        
		#msg_sign= bytes(msg,'utf-8')
		hashcode=hashlib.sha256(msg).hexdigest()
		binary = lambda x: "".join(reversed( [i+j for i,j in zip( *[ ["{0:04b}".format(int(c,16)) for c in reversed("0"+x)][n::2] for n in [1,0] ] ) ] ))
		xor = lambda x,y: ''.join([_xormap[a, b] for a, b in zip(x, y)])
        
		bin_str = binary(hashcode)
		
		result1 = ''
		for i in range(0, len(bin_str),16):
			starter = i
			c1 = bin_str[starter:starter+8] 
			c2 = bin_str[starter+8:starter+16] 
			result1+= xor(c1, c2)
        
		result2= ''
		for i in range(0,len(result1),16):
			starter = i
			c1 = result1[starter:starter+8] 
			c2 = result1[starter+8:starter+16] 
			result2+= xor(c1, c2)           
     
		result3= ''    
		for i in range(0,len(result2),16):
			starter = i  
			c1 = result2[starter:starter+8] 
			c2 = result2[starter+8:starter+16]   
			result3+= xor(c1, c2)


		return result3

	def keytrim(self, key):
		if len(key) == 32:
			return key
		if len(key) >= 32:
			return key[:32]
		else:
			return self._pad(key)

	def _pad(self, s, bs=32):
		return s + (bs - len(s) % bs) * chr(bs - len(s) % bs)

	def _unpad(self, s):
		return s[:-ord(s[len(s)-1:])]

	def utf8len(self,s):
		return len(s.encode('utf-8'))