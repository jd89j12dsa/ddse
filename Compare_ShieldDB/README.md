### Comparision with ShieldDB

This code converts our dataset into raw data that can be used on ShieldDB. 
Before the test, it is necessary to copy generated configuration files into the corresponding folders in ShieldDB.

## Dependency

Install ShieldDB, see more on [ShieldDB](https://github.com/MonashCybersecurityLab/ShieldDB).

```git clone https://github.com/MonashCybersecurityLab/ShieldDB.git```

NOTE: The RocksDB version mentioned in the original is out of date, please use RocksDB v6.22.1 and the corresponding gflags v2.2.2.

## Usage Instructions

1. move these files into ShieldDB, and make the "Var" folder:

```
mv ./ShieldDB_Supporter.py ./ShieldDB/
mv ./Gen.sh ./ShieldDB/
cd ./ShieldDB/
mkdir ./Var/
 ```

2. To make the transformed Crimes dataset, run shell code:
```
sh Gen.sh
``` 

3. Move the generated data from ./Var to related folders:
```
mv ./Var/DDSECrimeC/DDSECrimeC_cluster_dists.csv ./padding_distribution
mv ./Var/DDSECrimeC/DDSECrimeC_cluster_points.csv  ./padding_distribution
mv ./Var/DDSECrimeC/streaming ./
mv ./Var/DDSECrimeC/fixed_clusters_keywords ./a256
mv ./Var/DDSECrimeC/prob_clusters ./a256
```

4. Set the parameters in shield_setup.py:

```
line 41: alpha = 256
line 43: keyword_num = 34611
line 46: clusters_point_set="DDSECrimeC_cluster_points.csv"
line 47: clusters_dist = "DDSECrimeC_cluster_dists.csv"
line 48: alpha_data_set = [256,]
```



