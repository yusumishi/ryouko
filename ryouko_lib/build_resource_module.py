#! /usr/bin/env python

from os import chdir, system, path
chdir(path.dirname(path.realpath(__file__)))
system("pyrcc4 -o ./resources.py ./resources.qrc")