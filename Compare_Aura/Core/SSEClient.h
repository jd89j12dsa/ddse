//
// Created by shangqi on 2020/11/18.
//

#ifndef AURA_SSECLIENT_H
#define AURA_SSECLIENT_H

#include <thrift/protocol/TBinaryProtocol.h>
#include <thrift/transport/TBufferTransports.h>
#include <thrift/transport/TSocket.h>
#include <chrono>

#include "SSEClientHandler.h"
#include "../gen-cpp/SSEService.h"

using namespace server;
using namespace apache::thrift;
using namespace apache::thrift::concurrency;
using namespace apache::thrift::protocol;
using namespace apache::thrift::transport;
using namespace chrono;

class SSEClient {
private:
    uint8_t *key = (unsigned char*) "0123456789123456";
    uint8_t *iv = (unsigned char*) "0123456789123456";

    GGMTree *tree;
    BloomFilter<32, GGM_SIZE, HASH_SIZE> delete_bf;
    unordered_map<string, int> C;       // search time

    shared_ptr<TTransport> transport;
    SSEServiceClient *server;

public:
    SSEClient();
    ~SSEClient();
    size_t update_size;

    void update(OP op, const string& keyword, int ind);
    size_t get_updatesize();
    vector<int> search(const string& keyword);
};


#endif //AURA_SSECLIENT_H
