//
// Created by shangqi on 2020/11/18.
//

#ifndef AURA_SSESERVER_H
#define AURA_SSESERVER_H

#include <thrift/server/TSimpleServer.h>
#include <thrift/transport/TBufferTransports.h>
#include <thrift/transport/TSocket.h>

#include "SSEServerHandler.h"
#include "../GGM/GGMNode.h"
#include "../gen-cpp/SSEService.h"

using namespace server;
using namespace apache::thrift;
using namespace apache::thrift::concurrency;
using namespace apache::thrift::server;
using namespace apache::thrift::transport;

class SSEServer : public SSEServiceIf {
private:
    SSEServerHandler *handler;

public:
    SSEServer();
    void add_entries(const string& label, const string& tag, const vector<string>& ciphertext_list) override;
    void search(std::vector<int32_t>& _return, const string& token, const std::vector<SerialisedNode> & node_list, int32_t level) override;
};


#endif //AURA_SSESERVER_H
