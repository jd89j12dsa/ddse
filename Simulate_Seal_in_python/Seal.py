import  OMAP
import pymongo
import pdb
import time
import sys
from AdjORAM import AdjORAM


class Seal():

	def __init__(self, alpha, axe):
		self.alpha = alpha
		self.axe = axe
		self.OMAP_number = 1

	def adjpadding(self,x,dataset):
		
		M = []
		cnt = 0
		first_occur_dict = dict()
		for w in dataset:
			first_occur_dict[w] = cnt
			D_w = len(dataset[w])
			i = 1
			while D_w > x**i:
				i+=1

			dataset[w].extend(["-1"]*( x**i - D_w))
			cnt+= len(dataset[w])

			M.extend([ind for ind in dataset[w]])

		return M,first_occur_dict

	def Setup(self,dataset):

		ts = time.time()
		M,first_occur_dict = self.adjpadding(self.axe, dataset)
		Padding_time = time.time() - ts 


		ts = time.time()
		OMAP.Setup(self.OMAP_number, len(M))
		for w in dataset:
			cnt_w = len(dataset[w])
			OMAP.Ins(self.OMAP_number,w,str(first_occur_dict[w])+"|"+str(cnt_w))


		#pdb.set_trace()

		adjoram = AdjORAM(len(M), self.alpha)

		print("AdjORAM_Setup_success")

		Update_time = adjoram.Batchinsert(M)

		self.adjoram = adjoram

		Setup_time = time.time() - ts

		print("Setup_success")

		return Padding_time, Setup_time, Update_time

	def Search(self,w):

		s = OMAP.Find(self.OMAP_number,w)
		s = s.split("|")
		i_w, cnt_w = int(s[0]), int(s[1])
		result = []

		#pdb.set_trace()
		for i in range(i_w,i_w+cnt_w):

			r = self.adjoram.Access(i)
			result.append(r)

		return result