cmake_minimum_required(VERSION 3.16)
project(Aura)

set(CMAKE_CXX_STANDARD 14)

add_compile_options(-Wno-int-conversion)
add_compile_options(-Wno-implicit-function-declaration)

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
ADD_EXECUTABLE(AuraServer Core/SSEServer.cpp Core/SSEServerHandler.cpp GGM/GGMTree.cpp BF/Hash/SpookyV2.cpp Util/CommonUtil.c gen-cpp)
ADD_EXECUTABLE(AuraClient main.cpp Core/SSEClient.cpp GGM/GGMTree.cpp BF/Hash/SpookyV2.cpp Util/CommonUtil.c gen-cpp)

# link
TARGET_LINK_LIBRARIES(AuraServer OpenSSL::Crypto gen-cpp-thrift)
TARGET_LINK_LIBRARIES(AuraClient OpenSSL::Crypto gen-cpp-thrift)
