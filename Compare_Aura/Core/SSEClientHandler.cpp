#include "SSEClientHandler.h"

SSEClientHandler::SSEClientHandler() {
    server = new SSEServerHandler();
    // init the GGM Tree
    tree = new GGMTree(GGM_SIZE);
}

SSEClientHandler::~SSEClientHandler() {
    delete_bf.reset();
    delete server;
}

void SSEClientHandler::update(OP op, const string& keyword, int ind) {
    // compute the tag
    uint8_t pair[keyword.size() + sizeof(int)];
    memcpy(pair, keyword.c_str(), keyword.size());
    memcpy(pair + keyword.size(), (uint8_t*) &ind, sizeof(int));
    // generate the digest of tag
    uint8_t tag[DIGEST_SIZE];
    sha256_digest(pair, keyword.size() + sizeof(int), tag);
    // process the operator
    if(op == INS) {
        // get all offsets in BF
        vector<long> indexes = BloomFilter<32, GGM_SIZE, HASH_SIZE>::get_index(tag);
        sort(indexes.begin(), indexes.end());

        // get SRE ciphertext list
        vector<string> ciphertext_list;
        for(long index : indexes) {
            // derive a key from the offset
            uint8_t derived_key[AES_BLOCK_SIZE];
            memcpy(derived_key, key, AES_BLOCK_SIZE);
            GGMTree::derive_key_from_tree(derived_key, index, tree->get_level(), 0);
            // use the key to encrypt the id
            uint8_t encrypted_id[AES_BLOCK_SIZE + sizeof(int)];
            memcpy(encrypted_id, iv, AES_BLOCK_SIZE);
            aes_encrypt((uint8_t*) &ind, sizeof(int),
                        derived_key, encrypted_id,
                        encrypted_id + AES_BLOCK_SIZE);
            // save the encrypted id in the list
            ciphertext_list.emplace_back(string((char*) encrypted_id, AES_BLOCK_SIZE + sizeof(int)));
        }

        // token
        uint8_t token[DIGEST_SIZE];
        hmac_digest((uint8_t*) keyword.c_str(), keyword.size(),
                key, AES_BLOCK_SIZE,
                token);
        // label
        int counter = C[keyword];
        uint8_t label[DIGEST_SIZE];
        hmac_digest((uint8_t*) &counter, sizeof(int),
                token, DIGEST_SIZE,
                label);
        C[keyword]++;
        // convert tag/label to string
        string tag_str((char*) tag, DIGEST_SIZE);
        string label_str((char*) label, DIGEST_SIZE);
        // save the list on the server
        server->add_entries(label_str, tag_str, ciphertext_list);
    } else {
        // insert the tag into BF
        delete_bf.add_tag(tag);
    }
}

vector<int> SSEClientHandler::search(const string& keyword) {
    // token
//    cout << duration_cast<microseconds>(system_clock::now().time_since_epoch()).count() << endl;
    uint8_t token[DIGEST_SIZE];
    hmac_digest((uint8_t*) keyword.c_str(), keyword.size(),
                key, AES_BLOCK_SIZE,
                token);
    // search all deleted positions
    vector<long> bf_pos;
    for (int i = 0; i < GGM_SIZE; ++i) {
        bf_pos.emplace_back(i);
    }
    vector<long> delete_pos = delete_bf.search();
    vector<long> remain_pos;
    set_difference(bf_pos.begin(), bf_pos.end(),
            delete_pos.begin(), delete_pos.end(),
            inserter(remain_pos, remain_pos.begin()));
    // generate GGM Node for the remain position
    vector<GGMNode> node_list;
    node_list.reserve(remain_pos.size());
    for (long pos : remain_pos) {
        node_list.emplace_back(GGMNode(pos, tree->get_level()));
    }
    vector<GGMNode> remain_node = tree->min_coverage(node_list);
    // compute the key set and send to the server
    for(auto & i : remain_node) {
        memcpy(i.key, key, AES_BLOCK_SIZE);
        GGMTree::derive_key_from_tree(i.key, i.index, i.level, 0);
    }
    // give all results to the server for search
//    cout << duration_cast<microseconds>(system_clock::now().time_since_epoch()).count() << endl;
    vector<int> res = server->search(token, remain_node, tree->get_level());
//    cout << duration_cast<microseconds>(system_clock::now().time_since_epoch()).count() << endl;
    return res;
}