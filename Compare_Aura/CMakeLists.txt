cmake_minimum_required(VERSION 3.16)
project(Aura)

set(CMAKE_CXX_STANDARD 14)

FIND_PACKAGE(OpenSSL REQUIRED)

# build Thrift dependencies
set(THRIFT_FILE ${CMAKE_CURRENT_SOURCE_DIR}/Thrift/Server.thrift)
set(THRIFT_LIB_PATH /usr/local/lib/)

link_directories(${THRIFT_LIB_PATH})

exec_program("thrift --gen cpp -o ${CMAKE_CURRENT_SOURCE_DIR} ${THRIFT_FILE}")

add_library(gen-cpp-thrift STATIC
        gen-cpp/SSEService.cpp
        gen-cpp/Server_constants.cpp
        gen-cpp/Server_types.cpp)

target_link_libraries(gen-cpp-thrift -lthrift)

# load Aura header
INCLUDE_DIRECTORIES(. BF BF/Hash GGM Util gen-cpp)

# set executable outputs
ADD_EXECUTABLE(AESTest Test/AESTest.cpp Util/CommonUtil.c)
ADD_EXECUTABLE(BloomFilterTest Test/BloomFilterTest.cpp BF/Hash/SpookyV2.cpp)
ADD_EXECUTABLE(GGMTest Test/GGMTest.cpp GGM/GGMTree.cpp Util/CommonUtil.c)
ADD_EXECUTABLE(SSETest Test/SSETest.cpp Core/SSEClientHandler.cpp Core/SSEServerHandler.cpp GGM/GGMTree.cpp BF/Hash/SpookyV2.cpp Util/CommonUtil.c)
ADD_EXECUTABLE(AuraServer Core/SSEServer.cpp Core/SSEServerHandler.cpp GGM/GGMTree.cpp BF/Hash/SpookyV2.cpp Util/CommonUtil.c gen-cpp)
ADD_EXECUTABLE(AuraClient main.cpp Core/SSEClient.cpp GGM/GGMTree.cpp BF/Hash/SpookyV2.cpp Util/CommonUtil.c gen-cpp)

# link
TARGET_LINK_LIBRARIES(AESTest OpenSSL::Crypto)
TARGET_LINK_LIBRARIES(GGMTest OpenSSL::Crypto)
TARGET_LINK_LIBRARIES(SSETest OpenSSL::Crypto)
TARGET_LINK_LIBRARIES(AuraServer OpenSSL::Crypto gen-cpp-thrift)
TARGET_LINK_LIBRARIES(AuraClient OpenSSL::Crypto gen-cpp-thrift)
