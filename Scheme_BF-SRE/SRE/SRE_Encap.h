#include "GGMTree.h"
#include "BloomFilter.h"
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <iostream>
#include <string>
#include <vector>
#include <unordered_map>
#include <utility>

using namespace std;

struct DataPair {
    uint8_t tagString[DIGEST_SIZE];
    std::vector<std::string> ciphertext_list;
};

struct DataKrev{
    std::vector<GGMNode> node_list;
    int32_t level; 
};


class SRE_Encap
{
private:
    uint8_t *key = (unsigned char*) "0123456789123456";
    uint8_t *iv = (unsigned char*) "0123456789123456";
    int GGM_SIZE;
    int HASH_SIZE;
    GGMTree *tree;
    unordered_map<long, uint8_t*> keys;
    BloomFilter *delete_bf;




    void compute_leaf_keys(const vector<GGMNode>& node_list, int level);
    void set_compute_leaf_keys(const vector<GGMNode>& node_list_in, int level_in);
    bool compute_leaf_keys_next();

    vector<GGMNode> node_list;
    int level;
    int current_node_index;
    int current_i;


public:
	SRE_Encap(long ggm_size, int hash_size);
	~SRE_Encap();
	
    DataPair encrypt(int ind, uint8_t *tag);
    void revoke(uint8_t *tag);
    DataKrev Krev();

    vector<int> Dec(DataKrev& sKrev, vector<DataPair> datas);
    vector<int> Dec_Greed(DataKrev& sKrev, vector<DataPair> datas);
};