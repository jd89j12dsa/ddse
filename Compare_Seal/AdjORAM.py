import ORAM
import os
import time
import random
import pdb


class  AdjORAM(object):
	"""docstring for  AdjORAM"""

	def __npot(self,maxN):
		p = 1
		order = 0 
		while p<maxN:
			p <<= 1
			order+= 1
		return p, order

	def __init__(self, maxN, adjbit):

		self.key = b'Sixteen byte key'
		random.seed(self.key)
		self.maxdomain, self.maxbitorder = self.__npot(maxN)
		self.adjbit = adjbit
		self.PRPmaplist = self.__permute_and_split()
		self.ORAM_instance_maxnum = 1 << adjbit
		self.ORAM_instance_number = list()
		self.ORAM_input_list = {"samlpekey":[],}
		self.ORAM_instance_maxsize = 1
		if self.maxdomain > self.ORAM_instance_maxnum:
			self.ORAM_instance_maxsize = self.maxdomain // self.ORAM_instance_maxnum

	def __permute_and_split(self):

		new_lst = list(range(self.maxdomain)) 
		random.shuffle(new_lst)

		# pdb.set_trace()
		tuple_lst = []
		for x in new_lst:
			Oram_number = x
			Index_in_Oram = 1
			if self.maxbitorder-self.adjbit > 0:
				Oram_number = x >> (self.maxbitorder-self.adjbit)
				Index_in_Oram = x & ((1 << (self.maxbitorder-self.adjbit)) - 1)
			tuple_lst.append((Oram_number, Index_in_Oram))
		return tuple_lst

	def sort_dict_by_key(self,dict):
		sorted_keys = sorted(dict.keys())  
		sorted_values = [dict[key] for key in sorted_keys]
		return sorted_values

	
	def Batchinsert (self, datalist):


		resized_oram_input = dict()

		for i in range(len(datalist)):
			Oram_number, Index_in_Oram = self.PRPmaplist[i]

			if Oram_number not in resized_oram_input:
				resized_oram_input[Oram_number] = dict()

			resized_oram_input[Oram_number][Index_in_Oram] = datalist[i]
					
		te = []

		for Oram_number in resized_oram_input:

			values = self.sort_dict_by_key(resized_oram_input[Oram_number])
			values = [string[:min(4,len(string))] for string in values]
			
			ts = time.time()
			ORAM.BSetup(Oram_number,self.ORAM_instance_maxsize,values)
			te.append(time.time() - ts)

			self.ORAM_instance_number.append(Oram_number)

		return sum(te)/len(te)


	def Access(self, index):

		Oram_number, Index_in_Oram = self.PRPmaplist[index]

		if Oram_number not in self.ORAM_instance_number or Index_in_Oram > self.ORAM_instance_maxsize:

			return False

		value =  ORAM.Access(Oram_number,"r",Index_in_Oram,"")

		return value



		

