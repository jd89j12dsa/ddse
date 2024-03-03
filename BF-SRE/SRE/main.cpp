#include <iostream>
#include "SRE_Encap.h"
using namespace std;



int main()
{
    SRE_Encap sre(1024,5);
    uint8_t tag1[DIGEST_SIZE];
    vector<DataPair> datas;
    for(int i = 0; i < DIGEST_SIZE; i++)tag1[i] = 0;
    datas.emplace_back(sre.encrypt(1, tag1));
    uint8_t tag2[DIGEST_SIZE];
    for(int i = 0; i < DIGEST_SIZE; i++)tag2[i] = 0;
    tag2[0]=2;
    datas.emplace_back(sre.encrypt(2,tag2));
    sre.revoke(tag1);
    // sre.revoke(tag2);
    DataKrev sk = sre.Krev();
    vector <int> result = sre.Dec(sk,datas);
    for (auto r: result)
    {
        cout << r << endl;
    }
    result = sre.Dec_Greed(sk,datas);
    for (auto r: result)
    {
        cout << r << endl;
    }
    return 0;
}
