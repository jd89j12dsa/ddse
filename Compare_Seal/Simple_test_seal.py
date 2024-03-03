from Seal import Seal
import pdb


seal = Seal(2,2)
seal.Setup({"Hellow":["4111","3","2","2"],"World":["1","2","3"]})
print(seal.Search("Hellow"))
print(seal.Search("World"))