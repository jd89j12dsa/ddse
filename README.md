# d-DSE

d-DSE (Distinct Dynamic Searchable Symmetirc Encryption) is an ongoing program that aims to secure distinct search in EDB. 
We release our test code for future securtiy programs on EDB systems.


## How to Run
### Environment

Our experimental system is Ubuntu Server 16.04 x64

The python version is v3.6.0

### Install Basic Dependency

1. Install <u>MongoDB</u> (version 2.6.10) to provide datasets for various tests 

```sudo apt-get install mongodb```

2. Install <u>Pymongo</u> to read datasets

```pip3.6 install pymongo```

3. Install <u>MySQL</u>  to provide ciphertext storage

```sudo apt-get install mysql-server```

4. Install pymysql

```pip3.6 install pymysql```

5. Install openssldev libraries:

```sudo apt-get install libssl-dev```

### Datasets:

In DB_gen folder, we provide the Crimes, Wikipedia, and Enron datasets dumped from MongoDB.

To restore dumped dataset in MongoDB:

```
cd ./DB_Gen
  mongorestore --db (dataset_folder name) ./(dataset_folder name)
cd ../
```


### Tests:

Most codes provide shell commands in our test like:

```sh test_XXX.sh```

In detail, please see the dependency and useage instruction parts for each test:

[BF-SRE](BF-SRE/)


[Mitra$^P$](Compare_MITRAp/)


[Aura$^P$](Compare_AURAp/)


[Comparision with Seal](Compare_Seal/)


[Comparision with ShieldDB](Compare_ShieldDB/) 


## License

d-DSE is released under the [MIT License](./LICENSE).

## Contact

For any questions or inquiries regarding d-DSE, feel free to reach out to the project maintainers via email or open an issue on GitHub.
