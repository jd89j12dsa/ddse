# d-DSE

Welcome to d-DSE (Distinct Dynamic Symmetirc Encryption) project, an ongoing project that aims to secure distinct search. 
We release our test code for secutiy projects in continue.


## Attention

Now the source codes are for developer, which includes many dependeces such as MySQL, IPE, RocksDB, IPE, SRE, and so on. We will summarize the dependency requirements and provide simplified usages before July 4, 2023.


## Environment

Our experimental system is Ubuntu Server 16.04 x64

The python version is v3.6.0

## Install Basic Dependency

1. Install <u>MongoDB</u> to provide datasets for various tests 

```sudo apt-get install mongodb```

2. Install <u>Pymongo</u> to read datasets

```pip3.6 install pymongo```

3. Install <u>MySQL</u> to provide ciphertext storage

```sudo apt-get install mysql-server```

4. Install pymysql

```pip3.6 install pymysql```

5. Install openssldev libraries:

```sudo apt-get install libssl-dev```

## Datasets:


## Tests:

Most codes provide shell commands in our test like:

```sh test_XXX.sh```

In detail, please see the dependency and useage instruction parts in each tests:

[Heuristic from MITRA](Scheme_MITRAPP/README.md)


[BF-IPE](Scheme_BF-IPE-P/README.md)


[BF-SRE](Scheme_BF-SRE/README.md)


[Comparison from Seal](Simulate_Seal_in_python/README.md)


[Comparision from ShieldDB](Compare_ShieldDB/README.md)


[Query recover rate of d-DSE, Seal, and ShieldDB](BVA-BVMA-DDSE_ShielDB_Seal/README.md)


## Contributing


## License

d-DSE is released under the [MIT License](./LICENSE). Make sure to review the license terms before using or contributing to this project.

## Contact

For any questions or inquiries regarding d-DSE, feel free to reach out to the project maintainers via email or open an issue on GitHub.

We hope you find d-DSE project helpful and enjoy exploring the exciting world of encrypted database systems!
