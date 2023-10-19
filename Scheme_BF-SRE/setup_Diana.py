from distutils.core import setup, Extension

MOD = 'Diana'
setup(  name = MOD,
        version = '0.1',
        description= 'LiuB22',
        author = 'ldl',
        author_email = 'ldlkancolle@outlook.com',
        ext_modules = [Extension( MOD,
                                sources = ['Diana_Core_for_DDSE.c'],
                                extra_link_args = ['-lssl','-lcrypto'],
                                extra_compile_args = ['--std=c99','-w']
                                )
                                ]
    )
