#include "Core/SSEServerHandler.h"

SSEServerHandler::SSEServerHandler() {
    tags.clear();
    dict.clear();
}

void SSEServerHandler::add_entries(const string& label, const string& tag, vector<string> ciphertext_list) {
    tags[label] = tag;
    dict[label] = move(ciphertext_list);
}

vector<int> SSEServerHandler::search(uint8_t *token, const vector<GGMNode>& node_list, int level) {
    keys.clear();
    // pre-search, derive all keys
    compute_leaf_keys(node_list, level);
    // get the result
    int counter = 0;
    vector<int> res_list;
    while (true) {
        // get label string
        uint8_t label[DIGEST_SIZE];
        hmac_digest((uint8_t*) &counter, sizeof(int),
                    token, DIGEST_SIZE,
                    label);
        string label_str((char*) label, DIGEST_SIZE);
        counter++;
        // terminate if no label
        if(tags.find(label_str) == tags.end()) break;
        // get the insert position of the tag
        vector<long> search_pos = BloomFilter<32, GGM_SIZE, HASH_SIZE>::get_index((uint8_t*) tags[label_str].c_str());
        sort(search_pos.begin(), search_pos.end());
        // derive the key from search position and decrypt the id
        vector<string> ciphertext_list = dict[label_str];
        for (int i = 0; i < min(search_pos.size(), ciphertext_list.size()); ++i) {
            uint8_t res[4];
            if(keys[search_pos[i]] == nullptr) continue;
            aes_decrypt((uint8_t *) (ciphertext_list[i].c_str() + AES_BLOCK_SIZE), ciphertext_list[i].size() - AES_BLOCK_SIZE,
                        keys[search_pos[i]], (uint8_t *) ciphertext_list[i].c_str(),
                        res);
            if(*((int*) res) > 0) {
                res_list.emplace_back(*((int*) res));
            }
            break;
        }
    }
    return res_list;
}

void SSEServerHandler::compute_leaf_keys(const vector<GGMNode>& node_list, int level) {
    for(GGMNode node : node_list) {
        for (int i = 0; i < pow(2, level - node.level); ++i) {
            int offset = ((node.index) << (level - node.level)) + i;
            uint8_t derive_key[AES_BLOCK_SIZE];
            memcpy(derive_key, node.key, AES_BLOCK_SIZE);
            GGMTree::derive_key_from_tree(derive_key,  offset, level - node.level, 0);
            if(keys.find(offset) == keys.end()) {
                keys[offset] = (uint8_t*) malloc(AES_BLOCK_SIZE);
                memcpy(keys[offset], derive_key, AES_BLOCK_SIZE);
            }
        }
    }
}
