cmake_minimum_required(VERSION 3.0)

project(SRE)

FIND_PACKAGE(OpenSSL REQUIRED)

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


add_executable(SRE ${SOURCES})

# link
TARGET_LINK_LIBRARIES(SRE OpenSSL::Crypto)

