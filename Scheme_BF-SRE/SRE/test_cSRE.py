import cSRE
import pdb


cSRE.Setup(1,134,13)
cli = []
cli.append(cSRE.Enc(1,1,"World"))
cli.append(cSRE.Enc(1,2,"world"))
cli.append(cSRE.Enc(1,3,"Torld"))
cli.append(cSRE.Enc(1,4,"porld"))
cli.append(cSRE.Enc(1,5,"korld"))
cli.append(cSRE.Enc(1,6,"sorld"))
cli.append(cSRE.Enc(1,7,"Rorld"))
cSRE.Rev(1,"Torld")
cSRE.Rev(1,"world")
cSRE.Rev(1,"korld")
cSRE.Rev(1,"sorld")
cSRE.Rev(1,"Rorld")
sk = cSRE.sKey(1)
ret = cSRE.Dec(1,sk,cli)
print(ret)
ret = cSRE.DecG(1,sk,cli)
print(ret)
