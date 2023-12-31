from distutils.core import setup, Extension

MOD = 'DDSE2'
setup(  name = MOD,
        version = '0.1',
        description= '',
        author = '',
        author_email = '',
        ext_modules = [Extension( MOD,
                                sources = ['DDSE2_core.c'],
                                extra_link_args = ['-lssl','-lcrypto'],
                                extra_compile_args = ['--std=c99','-w']
                                )
                                ]
    )
