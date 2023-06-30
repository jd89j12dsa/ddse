# -*- coding: utf-8 -*-
from SRE_Boost import SRE
import pdb
import time
import threading

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

def complex_thread_decode_dec(skR,result):
		global sre
		dec_list = []
		for i in range(len(result)):
			ct = json.loads(result[i].decode('utf-8'))
			if sre.Dec_check(ct) == 0:
				dec_list.append(ct)
		output = []
		p = [MyThread(sre.Dec, (skR, dec_list[i])) for i in range(len(dec_list))]
		for t in p:
			t.start()
		for t in p:
			t.join()
		for t in p:
			if t.get_result() is not None:
				output.extend(t.get_result())
		return output


if __name__ == "__main__":
	s = SRE()
	s.init_keywordbf('hello',300,0.0001)
	ct_list = [s.Enc('hello',i,bytes('world'+str(i),'UTF-8')) for i in range(1,2000)]
	pdb.set_trace()
	
	s.Comp('hello',b'0')
	sk,skR = s.cKRev('hello')


	#pdb.set_trace()
	
	time_s = time.time()
	result = s.complex_process_dec('hello',skR,ct_list,16)
	#result = [s.Dec_line('hello',skR, ct) for ct in ct_list]
	time_e = time.time()
	print(time_e-time_s)

	print(result)
	s.Resetdeckey()
	