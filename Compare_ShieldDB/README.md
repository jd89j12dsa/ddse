### Support ShieldDB

This code converts our dataset into raw data that can be used on ShieldDB. 
After generation, it is necessary to copy the configuration file  of ShieldDB to the corresponding folders.

## Dependency

Install ShieldDB, see more on [ShieldDB](https://github.com/MonashCybersecurityLab/ShieldDB).

```git clone https://github.com/MonashCybersecurityLab/ShieldDB.git```

NOTE: The RocksDB is v6.22.1 and the corresponding gflags is v2.2.2.

## Usage Instructions

1. move these files into ShieldDB, and make the "Var" folder:

```
mv ./ShieldDB_Supporter.py ./ShieldDB/
mv ./Gen.sh ./ShieldDB/
cd ./ShieldDB/
mkdir ./Var/
 ```

2. To make the transformed Enron dataset, run shell code:
```
sh Gen.sh
``` 

3. Move the generated data from ./Var to related folders:
```
mv ./Var/Enron_USENIX/Enron_USENIX_cluster_dists.csv ./padding_distribution
mv ./Var/Enron_USENIX/Enron_USENIX_cluster_points.csv  ./padding_distribution
mv ./Var/Enron_USENIX/streaming ./
mv ./Var/Enron_USENIX/fixed_clusters_keywords ./data256
mv ./Var/Enron_USENIX/prob_clusters ./data256
```

4. Set the parameters in shield_setup.py:

```
line 41: alpha = 256
line 43: keyword_num = 16241
line 46: clusters_point_set="Enron_USENIX_cluster_points.csv"
line 47: clusters_dist = "Enron_USENIX_cluster_dists.csv"
line 48:alpha_data_set = [256,]
```



