#include "SRE_Encap.h"

SRE_Encap::SRE_Encap(long ggm_size, int hash_size) {

	tree = new GGMTree(ggm_size);
	delete_bf = new BloomFilter(32,ggm_size, hash_size);
	GGM_SIZE  = ggm_size;
	HASH_SIZE = hash_size;

}

SRE_Encap::~SRE_Encap(){
	delete_bf->reset();
}

DataPair SRE_Encap::encrypt(int ind, uint8_t *tag) {

    vector<long> indexes = BloomFilter(32, this->GGM_SIZE, this->HASH_SIZE).get_index(tag);
    sort(indexes.begin(), indexes.end());
    // get SRE ciphertext list
    DataPair data;

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
        data.ciphertext_list.emplace_back(string((char*) encrypted_id, AES_BLOCK_SIZE + sizeof(int)));
    }
    // convert tag/label to string
    memcpy(data.tagString, tag, DIGEST_SIZE);
    return data;
}

void SRE_Encap::revoke(uint8_t *tag){
    delete_bf->add_tag(tag);
}

DataKrev SRE_Encap::Krev(){

    // search all deleted positions
    vector<long> bf_pos;
    bf_pos.reserve(GGM_SIZE);
    for (int i = 0; i < GGM_SIZE; ++i) {
        bf_pos.emplace_back(i);
    }
    vector<long> delete_pos = delete_bf->search();
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
    for(auto & i : remain_node) {
        memcpy(i.key, key, AES_BLOCK_SIZE);
        GGMTree::derive_key_from_tree(i.key, i.index, i.level, 0);
    }
    
    DataKrev sKrev;

    sKrev.level = tree->get_level();
    sKrev.node_list = move(remain_node);

    return sKrev;
}



vector<int> SRE_Encap::Dec(DataKrev& sKrev, vector<DataPair> datas){

    // pre-search, derive all keys
    keys.clear();
    compute_leaf_keys(sKrev.node_list, sKrev.level);

    vector<int> res_list;
    for (auto data : datas)
    {
        vector<long> search_pos = BloomFilter(32, GGM_SIZE, HASH_SIZE).get_index(data.tagString);
        sort(search_pos.begin(), search_pos.end());
        // derive the key from search position and decrypt the id
        vector<string> ciphertext_list = data.ciphertext_list;
        for (int i = 0; i < min(search_pos.size(), ciphertext_list.size()); ++i) {
            if(keys[search_pos[i]] == nullptr) continue;
            uint8_t res[4];
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


vector<int> SRE_Encap::Dec_Greed(DataKrev& sKrev, vector<DataPair> datas){
    keys.clear();
    vector<int> res_list;
    set_compute_leaf_keys(sKrev.node_list, sKrev.level);
    for (auto data: datas)
    {
        vector<long> search_pos = BloomFilter(32, GGM_SIZE, HASH_SIZE).get_index(data.tagString);
        sort(search_pos.begin(), search_pos.end());
        vector<string> ciphertext_list = data.ciphertext_list;

        for (int i = 0; i < min(search_pos.size(), ciphertext_list.size()); ++i) {
            while(compute_leaf_keys_next() == true && keys[search_pos[i]] ==nullptr);
            if(keys[search_pos[i]] ==nullptr)continue;
            uint8_t res[4];
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


void SRE_Encap::set_compute_leaf_keys(const vector<GGMNode>& node_list_in, int level_in){
    this->node_list = move(node_list_in);
    this->level = level_in;
    this->current_i = 0;
    this->current_node_index = 0;
}


bool SRE_Encap::compute_leaf_keys_next() {
    while (current_node_index < node_list.size()) {
        GGMNode node = node_list[current_node_index];
        while (current_i < pow(2, level - node.level)) {
            int offset = ((node.index) << (level - node.level)) + current_i;
            uint8_t derive_key[AES_BLOCK_SIZE];
            memcpy(derive_key, node.key, AES_BLOCK_SIZE);
            GGMTree::derive_key_from_tree(derive_key,  offset, level - node.level, 0);
            if(keys.find(offset) == keys.end()) {
                keys[offset] = (uint8_t*) malloc(AES_BLOCK_SIZE);
                memcpy(keys[offset], derive_key, AES_BLOCK_SIZE);
            }
            current_i++;
        }
        current_i = 0;
        current_node_index++;
    }
    return current_node_index < node_list.size();
}



void SRE_Encap::compute_leaf_keys(const vector<GGMNode>& node_list, int level){
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