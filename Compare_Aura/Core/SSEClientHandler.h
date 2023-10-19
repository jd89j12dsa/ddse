//
// Created by shangqi on 2020/6/17.
//

#ifndef AURA_SSECLIENTHANDLER_H
#define AURA_SSECLIENTHANDLER_H

#include "GGMTree.h"
#include "Core/SSEServerHandler.h"

enum OP {
    INS, DEL
};

class SSEClientHandler {
private:
    uint8_t *key = (unsigned char*) "0123456789123456";
    uint8_t *iv = (unsigned char*) "0123456789123456";

    GGMTree *tree;
    BloomFilter<32, GGM_SIZE, HASH_SIZE> delete_bf;
    unordered_map<string, int> C;       // search time

    SSEServerHandler *server;
public:
    SSEClientHandler();
    ~SSEClientHandler();
    void update(OP op, const string& keyword, int ind);
    vector<int> search(const string& keyword);
};


#endif //AURA_SSECLIENTHANDLER_H
