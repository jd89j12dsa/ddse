from distutils.core import setup, Extension

MOD = 'cSRE'

extension_mod = Extension( MOD, sources = ['cSRE.cpp','SRE_Encap.cpp','CommonUtil.c','GGMTree.cpp','./Hash/SpookyV2.cpp'],
                libraries = ["ssl","crypto"],
                include_dirs = ['./','./Hash'],
                extra_compile_args = ["-I/usr/local/include/openssl"],
                extra_link_args = ["-L/usr/local/lib"]
        )

setup(  name = MOD,
        version = '0.1',
        description= '',
        author = '',
        author_email = '',
        ext_modules = [extension_mod,]
    )
