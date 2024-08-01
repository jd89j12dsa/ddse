# docker build -t ubuntu1604py36
FROM ubuntu:16.04

ENV DEBIAN_FRONTEND=noninteractive

# --- Update and install dependencies ---
RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    curl \
    build-essential \
    apt-transport-https \
    lsb-release \
    ca-certificates \
    mysql-server-5.7 \
    automake \
    bison \
    flex \
    g++ \
    git \
    libboost-all-dev \
    libevent-dev \
    libssl-dev \
    libtool \
    make \
    pkg-config \
    python3-dev \
    mongodb \
    libsnappy-dev \
    zlib1g-dev \
    libbz2-dev \
    libgflags-dev \
    liblz4-dev \
    python-virtualenv \
    python-dev \
    zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Build python3.6 from source
RUN wget https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tgz && \
    tar -xvzf Python-3.6.3.tgz && \
    cd Python-3.6.3 && \
    ./configure && \
    make -j && \
    make install && \
    cd .. && \
    rm -rf Python-3.6.3.tgz Python-3.6.3

# Build Apache Thrift 0.13.0
RUN wget https://archive.apache.org/dist/thrift/0.13.0/thrift-0.13.0.tar.gz && \
    tar -xvzf thrift-0.13.0.tar.gz && \
    cd thrift-0.13.0 && \
    ./configure && \
    make -j && \
    make install && \
    cd .. && \
    rm -rf thrift-0.13.0.tar.gz thrift-0.13.0

# Build cmake 3.17 from source
RUN wget -SL https://github.com/Kitware/CMake/releases/download/v3.17.0-rc3/cmake-3.17.0-rc3.tar.gz && \
    mkdir -p cmake-3.17.0-rc3.src && \
    tar -xvf cmake-3.17.0-rc3.tar.gz --strip-components=1 -C cmake-3.17.0-rc3.src && \
    cd cmake-3.17.0-rc3.src && \
    ./bootstrap && \
    make -j && \
    make install && \
    cd .. && \
    rm -rf cmake-3.17.0-rc3.tar.gz cmake-3.17.0-rc3.src

# --- Start artifact install ---

# Clone the artifact repository
RUN git clone https://github.com/jd89j12dsa/ddse /ddse


# Start DB
RUN mkdir -p /data/db

CMD ["bash"]


## Start installation
WORKDIR /ddse/BF-SRE
RUN python3.6 setup_DDSE2.py install && \
    python3.6  setup_Diana.py install && \
    cd ./SRE && \
    python3.6 cSRE_setup.py install && \
    cd .. && \
    pip3.6 install --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org pathos

WORKDIR /ddse/Compare_MITRAp
RUN python3 setup_MITRAPP.py install && \
    python3 setup_MITRAPP.py install

WORKDIR /ddse/Compare_AURAp/build
RUN cmake .. && \
    make


WORKDIR /ddse/Compare_Seal
RUN wget https://archives.boost.io/release/1.64.0/source/boost_1_64_0.tar.gz && \ 
    tar -xvzf boost_1_64_0.tar.gz && \
    cd boost_1_64_0 && \
    ./bootstrap.sh --prefix=/usr/local && \
    ./b2  && \
    ./b2  install && \
    cd .. 


WORKDIR /ddse/Compare_Seal
RUN python3.6 setup_OMAP.py install && \
    python3.6 setup_ORAM.py install

WORKDIR /ddse/Compare_ShieldDB
RUN git clone https://github.com/MonashCybersecurityLab/ShieldDB.git && \
    git clone https://github.com/facebook/rocksdb.git && \
    cd rocksdb && \
    git checkout v6.22.1 && \
    mkdir build && \
    cd build && \
    cmake .. && \
    make -j && \
    cd .. && \
    export CPLUS_INCLUDE_PATH=${CPLUS_INCLUDE_PATH}${CPLUS_INCLUDE_PATH:+:}$(pwd)/include && \
    export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}${LD_LIBRARY_PATH:+:}$(pwd)/build/ && \
    export LIBRARY_PATH=${LIBRARY_PATH}${LIBRARY_PATH:+:}$(pwd)/build/ && \
    virtualenv pyrocks_test && \
    cd pyrocks_test && \
    . ./bin/activate && \
    pip3.6 install  --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org Cython==0.29.35 &&\
    pip3.6 install  --trusted-host pypi.org --trusted-host pypi.python.org --trusted-host files.pythonhosted.org python-rocksdb==0.7.0 && \
    cd /ddse/Compare_ShieldDB && \
    mv ./ShieldDB_Supporter.py ./ShieldDB/ && \
    mv ./Gen.sh ./ShieldDB/  && \
    cd ./ShieldDB/ && \
    mkdir ./Var/


# Set the default command to bash
WORKDIR /ddse/
CMD ["bash"]



