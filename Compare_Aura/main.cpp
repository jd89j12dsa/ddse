#include "Core/SSEClient.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <chrono>

using namespace chrono;


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
        // 检查当前元素是否已经存在于结果向量中
        if (std::find(resultVector.begin(), resultVector.end(), real_num) == resultVector.end()) {
            // 如果不存在，将其添加到结果向量中
            resultVector.push_back(real_num);
        }
    }
    return resultVector;
}



int main(int argc, char* argv[]) {


    std::ifstream dup(argv[3],std::ifstream::in);

    if (!dup) {
        std::cerr << "无法打开文件." << std::endl;
        return 1;
    } 

    std::map<int,int> restore;
    int rev_num,fake_id,real_id;

    dup>>rev_num;

    // 逐行读取字符串
    while (dup>>fake_id>>real_id) {
        restore[fake_id] = real_id;
    }    

    dup.close();

    std::ifstream file(argv[1],std::ifstream::in);  // 替换为实际文件路径

    cout << "read " << argv[1] <<endl;

    if (!file) {
        std::cerr << "无法打开文件." << std::endl;
        return 1;
    }

    int numRecords;
    file >> numRecords;  // 读取操作记录的数量

    std::vector<Record> records;

    std::string line;
    std::string part1;
    int part2,part3;
    std::getline(file, line);

    // 逐行读取操作记录
    for (int i = 0; i < numRecords; ++i) {
        std::getline(file, line);  // 读取一行操作记录
        // cout<< line << endl;
        std::istringstream iss(line);
        if (!(iss >> part1 >> part2 >> part3)) {
            std::cerr << "解析操作记录时发生错误." << std::endl;
            return 1;
        }

        Record record = {part1,part2,part3};
        records.push_back(record);
    }

    file.close();

    auto start = std::chrono::steady_clock::now();

    SSEClient client;

    auto end = std::chrono::steady_clock::now();

    auto tt = std::chrono::duration_cast<microseconds>(end-start);
    cout << "Setup " << tt.count() << "us" << endl;

    start = std::chrono::steady_clock::now();

    auto min_start = std::chrono::steady_clock::now();
    auto min_end = std::chrono::steady_clock::now();
    auto min_tt = std::chrono::duration_cast<microseconds>(min_end-min_start);
    std::map<int,int> volume_update;
    int cahc;
    for (int i = 0; i < records.size(); ++i) {
        const Record& record = records[i];
        // cout<< "Update " <<  record.part2 << " " << record.part3;
        // auto startu = std::chrono::steady_clock::now();
        const std::string str = std::to_string(record.part2);

        min_start = std::chrono::steady_clock::now();
        if (record.part1 == "INS")client.update(INS, str, record.part3);
        else client.update(DEL, str, record.part3);
        min_end = std::chrono::steady_clock::now();
        min_tt = std::chrono::duration_cast<microseconds>(min_end-min_start);
        cahc = int(min_tt.count());

        auto it = volume_update.find(record.part2);

        if (it != volume_update.end()) {
        // 找到了
            it->second += cahc;
        } else {
        // 没找到
            volume_update[record.part2] = cahc;
        }
        // auto endu = std::chrono::steady_clock::now();
        // auto ttu = std::chrono::duration_cast<microseconds>(endu-startu);
        // cout<< " " << ttu.count() << "us" << endl;
    }

    end = std::chrono::steady_clock::now();

    tt = std::chrono::duration_cast<microseconds>(end-start);
    cout << "Update " << tt.count() << "us" << endl;
    cout << "Update Size" << client.get_updatesize() << "bytes" << endl;

    for (const auto &pair : volume_update) {
        std::cout << "Keyword: \t" << pair.first << "\t, Value: \t" << pair.second << std::endl;
    }

    cout << argv[2] << endl;
    std::ifstream task(argv[2],std::ifstream::in);  // 替换为实际文件路径

    if (!task) {
        std::cerr << "无法打开文件." << std::endl;
        return 1;
    }

    std::vector<int> values;
    int value;

    // 逐行读取字符串
    while (task>>value) {
        values.push_back(value);
    }

    task.close();

    for (int i = 0; i < values.size(); ++i) {

    start = std::chrono::steady_clock::now();
    const std::string str = std::to_string(values[i]);
    std::vector<int> results = client.search(str);
    end = std::chrono::steady_clock::now();
    tt = std::chrono::duration_cast<microseconds>(end-start);
    auto start1 = std::chrono::steady_clock::now();
    std::vector<int> resultVector = removeDuplicates(results,restore);
    auto end1 = std::chrono::steady_clock::now();
    auto tt1 = std::chrono::duration_cast<microseconds>(end1-start1);


    cout << str << '\t' << "Search_D" << '\t'<< tt1.count() << "\tus" << resultVector.size() << "\t" << "Search_S" << '\t' << values[i] << '\t' << results.size() << '\t' << tt.count() << '\t' << "us" << endl;

    }

    return 0;
}