#include "Core/SSEClient.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <cstdlib>
#include <chrono>

using namespace chrono;


SSEClient client;
std::map<int,int> restore;

struct Record {
    const std::string part1;
    int part2;
    int part3;
};


std::vector<int> removeDuplicates(const std::vector<int>& inputVector, std::map<int,int>& inputMap) {
    std::vector<int> resultVector;


    for (const int& num : inputVector) {
        int real_num; 
        if (num>= 20000000) continue;
        real_num = inputMap[num];
        if (std::find(resultVector.begin(), resultVector.end(), real_num) == resultVector.end()) {
            resultVector.push_back(real_num);
        }
    }
    return resultVector;
}


int estimateBFsize(int n, double p) {
    int bitSize = static_cast<int>(-n * log(p) / pow(log(2), 2));
    int hashFuncSize = static_cast<int>(bitSize * log(2) / n);
    return bitSize;
}



int search_the_DB(char* ca1, int ia2)
{

// Search test

    char name3[300] = {0};
    strcpy(name3,ca1);
    strcat(name3,"Search");

    
    std::ifstream task(name3,std::ifstream::in);  

    if (!task) {
        std::cerr << "fail read search." << std::endl;
        return 1;
    }

    std::vector<int> values;
    int value;

    if(ia2 == 0) {
    while (task>>value) {
        values.push_back(value);
    }}

    else{
        task>>value;
        values.push_back(value);
    }

    task.close();

    cout<< "Client_cost(us)\tKeyword\tRemove_dup(us)\tTotal_cost(us)\tCommu_size" << endl;


    int search_range = values.size();
    
    if (ia2>0) {
        search_range = 1;
    }

    for (int i = 0; i < search_range; ++i) {

    auto start = std::chrono::steady_clock::now();
    const std::string str = std::to_string(values[i]);
    std::vector<int> results = client.search(str);
    auto end = std::chrono::steady_clock::now();
    auto tt = std::chrono::duration_cast<microseconds>(end-start);
    auto start1 = std::chrono::steady_clock::now();
    int Commu_size = results.size()*80; // the size of minimal AES cipher in UNI-CODE
    std::vector<int> resultVector = removeDuplicates(results,restore);
    auto end1 = std::chrono::steady_clock::now();
    auto tt1 = std::chrono::duration_cast<microseconds>(end1-start1);


    cout << 'F' << str << '\t' << tt1.count() << "\t" << tt.count() << '\t' << Commu_size << endl;

    }

    return 1;
}


int main(int argc, char* argv[]) {


    char name[300] = {0};
    strcpy(name,argv[1]);
    strcat(name,"REV");

    std::ifstream dup(name,std::ifstream::in);

    if (!dup) {
        std::cerr << "fail read REV." << std::endl;
        return 1;
    } 

    int rev_num,fake_id,real_id;

    dup>>rev_num;

    while (dup>>fake_id>>real_id) {
        restore[fake_id] = real_id;
    }    

    dup.close();

    char name2[300] = {0};
    strcpy(name2,argv[1]);
    strcat(name2,"DB");
    strcat(name2,argv[2]);

    std::ifstream file(name2,std::ifstream::in);  

    cout << "read " << name2 <<endl;

    if (!file) {
        std::cerr << "fail read DB." << std::endl;
        return 1;
    }

    int numRecords;
    file >> numRecords;  

    std::vector<Record> records;

    std::string line;
    std::string part1;
    int part2,part3;
    std::getline(file, line);

    for (int i = 0; i < numRecords; ++i) {
        std::getline(file, line);  
        // cout<< line << endl;
        std::istringstream iss(line);
        if (!(iss >> part1 >> part2 >> part3)) {
            std::cerr << "fail." << std::endl;
            return 1;
        }

        Record record = {part1,part2,part3};
        records.push_back(record);
    }

    file.close();

    auto start = std::chrono::steady_clock::now();

    auto end = std::chrono::steady_clock::now();

    auto tt = std::chrono::duration_cast<microseconds>(end-start);
    cout << "Setup " << tt.count() << "us" << endl;

    start = std::chrono::steady_clock::now();

    auto min_start = std::chrono::steady_clock::now();
    auto min_end = std::chrono::steady_clock::now();
    auto min_tt = std::chrono::duration_cast<microseconds>(min_end-min_start);
    std::map<int,int> volume_update;
    std::map<int,int> volume_update_storage;
    int cahc;
    int del_count = 0;
    int iargv2 = std::stoi(argv[2]);
    int iargv3 = std::stoi(argv[3]);
    for (int i = 0; i < records.size(); ++i) {
        const Record& record = records[i];
        const std::string str = std::to_string(record.part2);

        min_start = std::chrono::steady_clock::now();
        if (record.part1 == "INS")client.update(INS, str, record.part3);
        else {
            client.update(DEL, str, record.part3);
            del_count+=1;
             }
        min_end = std::chrono::steady_clock::now();
        min_tt = std::chrono::duration_cast<microseconds>(min_end-min_start);
        cahc = int(min_tt.count());

        auto it = volume_update.find(record.part2);
        auto it2 = volume_update_storage.find(record.part2);

        if (it != volume_update.end()) {
            it->second += cahc;
            it2->second += 1;
        } else {
            volume_update[record.part2] = cahc;
            volume_update_storage[record.part2] = 1;
        }

        if (del_count == iargv3 && iargv2 > 0)
            {
                del_count = 0;
                search_the_DB(argv[1], iargv2);
            }

    }

    end = std::chrono::steady_clock::now();
    tt = std::chrono::duration_cast<microseconds>(end-start);



    std::cout << "Keyword\tUpdate_time(us)\tStorage(bytes)" << std::endl;
    std::cout << "None\tNone\t" << AES_BLOCK_SIZE*3 << std::endl;

    for (const auto &pair : volume_update) {
        int storage =  estimateBFsize(volume_update_storage[pair.first],0.0001)/8 + AES_BLOCK_SIZE + sizeof(int)*2;
        std::cout <<"F" << pair.first << "\t" << pair.second << "\t" << storage << std::endl;
    }


    if(std::stoi(argv[3]) == 0) {
        search_the_DB(argv[1], 0);
    }

    
    return 0;
}
