Compare Aura

## Requirements

* Git
* Ubuntu 16.04
* g++-7 (7.5.0 in ubuntu 18.04)
* cmake 3.17
* openssl 1.0.2
* Apache Thrift 0.13.0

## Building

```
cd build
# use cmake/make to build the code
cmake ..
make
```
## Usage
We provide a shell command for keyword search time cost without deletion on Crime dataset:

```
cd dataset
python3.6 Aura_plan.py Crime_USENIX_REV
cd ..
sh ./test.sh

```
