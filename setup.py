#! /usr/bin/env python

files = ["icons/*", "*.*"]

from distutils.core import setup

setup(
    name = 'ryouko',
    version = '0.5.0',
    description = 'PyQt4 Web browser',
    long_description = """Ryouko is a basic PyQt4 Web browser. It was coded for fun and is not intended for serious usage, but it should be capable of fulfilling very basic browsing needs.""",
    scripts = ['ryouko'],
    packages = ['ryouko_lib'],
    package_data = {'ryouko_lib' : files },
    author = 'Daniel Sim',
    author_email =  'foxhead128@gmail.com',
    url = "http://sourceforge.net/projects/ryouko/",
    license = "MIT"
)
