import ORAM,pdb
ORAM.BSetup(1,10,["1","world"])
ORAM.BSetup(2,10,["cong","rulation"])
print(ORAM.Access(1,"w",0,"Hello"))

print(ORAM.Access(1,"r",0,""))
print(ORAM.Access(1,"r",1,""))
print(ORAM.Access(2,"r",0,""))
print(ORAM.Access(2,"r",1,""))