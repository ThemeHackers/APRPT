import os
import sys
from setuptools import setup, Extension, find_packages

ext_modules = []
if sys.platform.startswith('linux'):
    mod1 = Extension('apybluez.bluetooth._bluetooth',
                     libraries = ['bluetooth'],
                     sources = ['bluez/btmodule.c', 'bluez/btsdp.c'])
    ext_modules.append(mod1)

setup(name='apybluez',
      version='0.1.0',
      description='Apple Protocol Research Framework based on PyBluez',
      ext_modules=ext_modules,
      packages=['apybluez', 'apybluez.bluetooth', 'apybluez.apple', 'apybluez.hci'],
      package_dir={'apybluez': '.'},
      install_requires=['rich', 'pycryptodome'],
)
