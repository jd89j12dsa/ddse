from distutils.core import setup, Extension

MOD = 'ORAM'
setup(  name = MOD,
        version = '0.1',
        description= '',
        author = '',
        author_email = '',
        ext_modules = [Extension( MOD,
                                sources = ['Encap_ORAM.cpp','OMAP.cpp','ORAM.cpp',
                                'RAMStore.cpp','AES.cpp','Bid.cpp','AVLTree.cpp',
                                'Utilities.cpp'],
                                include_dirs = ['./'],
                                extra_link_args = ['-lssl','-lcrypto'],
                                extra_compile_args = ['--std=c++11']
                                )
                                ]
    )
