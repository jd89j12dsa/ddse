# CMake 最低版本要求
cmake_minimum_required(VERSION 3.0)

# 项目名称
project(SRE)

FIND_PACKAGE(OpenSSL REQUIRED)

# 添加源文件

set(syslib /usr/local/lib/)

link_directories(${syslib})

set(SOURCES
    SRE_Encap.cpp
    main.cpp
    CommonUtil.c
    GGMTree.cpp
    Hash/SpookyV2.cpp

)

INCLUDE_DIRECTORIES(. BF BF/Hash)


# 生成可执行文件
add_executable(SRE ${SOURCES})

# link
TARGET_LINK_LIBRARIES(SRE OpenSSL::Crypto)

