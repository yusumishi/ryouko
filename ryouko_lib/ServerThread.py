#! /usr/bin/env python

from __future__ import print_function
import os.path, sys
from os import chdir
from PyQt4 import QtCore
from SimpleHTTPServer import test
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)

class ServerThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.url = ""
        self.directory = ""
    def setDirectory(self, directory):
        self.directory = directory
    def run(self):
        if os.path.exists(self.directory):
            chdir(self.directory)
            test()
