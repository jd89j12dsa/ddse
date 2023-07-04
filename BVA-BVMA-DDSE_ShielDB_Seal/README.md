### Query recovery of d-DSE, Seal, and ShielDB

We forked the code for testing query recovery rate in [USENIX23](https://github.com/Kskfte/BVA-BVMA).
The Wikipedia dataset is decoded by ```leak. py```, and we conducted tests on d-DSE, Seal, and ShieldDB, respectively. 

## Dependency

Install numpy,tqdm

```
pip3.6 install numpy
pip3.6 install tqdm
```


## Usage Instructions

We provide the test example when the target query number is 5000.
To start the test, run the shell code in the current folder:

```sh test_recover.sh```
