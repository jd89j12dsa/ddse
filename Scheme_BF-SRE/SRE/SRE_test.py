# -*- coding: utf-8 -*-
from SRE import SRE
import pdb
import time
s = SRE()
ct_list = s.Enc('hello',9,b'world')
s.Comp(b'0')
sk,skR = s.cKRev('hello')
print(hash(str(skR)))

time_s = time.time()
print(s.Dec(skR,ct_list))
time_e = time.time()
print(time_e-time_s)