#! /usr/bin/env python

import os

app_lib = os.path.dirname(os.path.realpath(__file__))
app_info = os.path.join(app_lib, "ryouko_lib", "info.txt")
app_version = '0.11.7'
if os.path.exists(app_info):
    readVersionFile = open(app_info, "r")
    metadata = readVersionFile.readlines()
    readVersionFile.close()
    if len(metadata) > 0:
        app_version = metadata[0].rstrip("\n")

os.chdir(app_lib)
os.system("DEBFULLNAME=foxhead128; export DEBFULLNAME")
os.system("DEBEMAIL=foxhead128@gmail.com; export DEBEMAIL")
os.system("debchange --create --package ryouko -v " + app_version)
