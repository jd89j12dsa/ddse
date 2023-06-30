import OMAP
OMAP.Setup(1,10)
OMAP.Setup(30,10)
OMAP.Ins(1,"1","5")
OMAP.Ins(30,"2","10")
print(OMAP.Find(1,"1"))
print(OMAP.Find(30,"2"))