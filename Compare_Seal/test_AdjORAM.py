from AdjORAM import AdjORAM

aORAM = AdjORAM(1,5)
aORAM.Batchinsert(["1","2","3","4","5"])
print(aORAM.Access(3))
print(aORAM.Access(0))