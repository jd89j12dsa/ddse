### Support ShieldDB

This code converts our database into raw data that can be used on ShieldDB. 
After generation, it is necessary to copy the configuration file and the parameters of ShielDB to the corresponding file location.

## Dependency

Install ShieldDB, see more on [ShieldDB](https://github.com/MonashCybersecurityLab/ShieldDB).

```git clone https://github.com/MonashCybersecurityLab/ShieldDB.git```

## Usage Instructions

1. move these files into ShieldDB, and make var folder:

```
mv ./ShieldDB_Supporter.py ./ShieldDB/
mv ./Gen.sh ./ShieldDB/
cd ./ShieldDB/
mkdir ./Var/
 ```

2. To make the transformed Wikipedia dataset, run shell code:
```
sh Gen.sh
``` 

3. Move the generated data from ./Var to related folders.




