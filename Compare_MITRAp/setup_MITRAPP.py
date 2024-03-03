from distutils.core import setup, Extension

MOD = 'MITRAPP'
setup(  name = MOD,
        version = '0.1',
        description= '',
        author = '',
        author_email = '',
        ext_modules = [Extension( MOD,
                                sources = ['MITRAPP_core.c'],
                                extra_link_args = ['-lssl','-lcrypto'],
                                extra_compile_args = ['--std=c99','-w']
                                )
                                ]
    )
