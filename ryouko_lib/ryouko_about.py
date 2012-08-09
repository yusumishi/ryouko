#! /usr/bin/env python

import os.path, sys

try: __file__
except: __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))

app_info = os.path.join(app_lib, "info.txt")
app_version = "N/A"
app_codename = "N/A"
if os.path.exists(app_info):
    readVersionFile = open(app_info)
    metadata = readVersionFile.readlines()
    readVersionFile.close()
    if len(metadata) > 0:
        app_version = metadata[0].rstrip("\n")
        if len(metadata) > 1:
            app_codename = metadata[1].rstrip("\n")
app_commandline = ""
for arg in sys.argv:
    app_commandline = "%s%s " % (app_commandline, arg)