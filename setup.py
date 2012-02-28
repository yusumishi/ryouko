#! /usr/bin/env python

files = ["icons/*", "*.*"]

from distutils.core import setup

setup(
    name = 'ryouko',
    version = '0.4.2',
    description = 'PyQt4 Web browser',
    long_description = """Ryouko is a basic PyQt4 Web browser.""",
    scripts = ['ryouko'],
    packages = ['ryouko_lib'],
    package_data = {'ryouko_lib' : files },
    author = 'Daniel Sim',
    author_email =  'foxhead128@gmail.com',
    url = "http://sourceforge.net/projects/fh-miscellany/",
    license = "MIT"
)
