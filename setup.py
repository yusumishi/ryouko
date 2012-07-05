#! /usr/bin/env python

files = ["translations/*", "icons/*", "*.*"]

import os.path
from distutils.core import setup

app_lib = os.path.dirname(os.path.realpath(__file__))
app_info = os.path.join(app_lib, "ryouko_lib", "info.txt")
app_version = '0.6.5'
if os.path.exists(app_info):
    readVersionFile = open(app_info, "r")
    metadata = readVersionFile.readlines()
    readVersionFile.close()
    if len(metadata) > 0:
        app_version = metadata[0].rstrip("\n")

setup(
    name = 'ryouko',
    version = app_version,
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
