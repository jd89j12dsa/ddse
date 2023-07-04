### BF-IPE test


## Dependency

1. Install the python-C models for BF-IPE.

```  
sudo python3.6 setup_DDSE3.py install
sudo python3.6 setup_Diana.py install
```

2. Install pathos module.

```
pip3.6 install pathos
```

3. Install optimized FH-IPE module. 

  a. Fork the FH-IPE in current folder, please see more information about [FH-IPE](https://github.com/kevinlewi/fhipe.git) installation.

```
git clone --recursive https://github.com/kevinlewi/fhipe.git
cd fhipe
sudo make install
```

  b. Replace the original ipe.py with the optmized version


```
cd ..
mv ./ipe.py ./fhipe/fhipe/
```

## Usage Instructions


We provide an exmaple for BF-IPE on the VAERS dataset without deletion operations.

To start the test, run the shell code in the current folder:

```sh test_BF-IPE.sh```
