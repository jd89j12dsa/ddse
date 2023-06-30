#coding=utf-8
import Diana
import MITRAPP
import pdb

dur, ownerkey, keyleft, keyright = Diana.Setup() 
dur, session=MITRAPP.PRF(ownerkey,'hello123456789012345678901234567890')
dur, cipher = MITRAPP.AESEncrypt(session,'6137216516305998566$0ins%%%%%%%%')

print (cipher)
dur, plain = MITRAPP.AESDecrypt(session,cipher)
print (plain)
