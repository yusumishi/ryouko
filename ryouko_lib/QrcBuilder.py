#! /usr/bin/env python

from __future__ import print_function
import os.path  
from os import listdir, system
from PyQt4.QtCore import QResource

def chop(a, b):
    if a.startswith(b):
        c = a[len(b):len(a)]
        return c
    else:
        return a

class QrcBuilder():
    def __init__(self, parent=None):
        #QtCore.QThread.__init__(self, parent)
        self.url = ""
        self.directory = ""
    def setDirectory(self, directory):
        self.directory = directory
    def start(self):
        contents = """<!DOCTYPE RCC><RCC version="1.0">
 <qresource>\n"""
        contents = contents + self.buildlist(False, "extensions")
        contents = contents + """ </qresource>
 </RCC>"""
        #print(contents)
        f = open(os.path.join(self.directory, "extensions.qrc"), "w")
        f.write(contents)
        f.close()
        system("pyrcc4 -o \"" + os.path.join(self.directory, "extensions.py") + "\" \"" + os.path.join(self.directory, "extensions.qrc") + "\"")
    def buildlist(self, dirname=False, exactdir=False):
        contents = ""
        if not dirname:
            dirname = self.directory
        l = listdir(dirname)
        for fname in l:
            bork = False
            if exactdir:
                if exactdir != fname:
                    bork = True
            if not bork:
                if os.path.isdir(os.path.join(dirname, fname)):
                    contents = contents + self.buildlist(os.path.join(dirname, fname))
                else:
                    contents = contents +\
                    "     <file>" + chop(os.path.join(dirname, fname).replace(self.directory, "").replace("\\\\", "/").replace("\\", "/"), "/") + "</file>\n"
        return contents
    def recursive_listdir(dirname):
        l = listdir(dirname)
        for fname in l:
            if os.path.isdir(fname):
                l2 = recursive_listdir(os.path.join(dirname, fname))

if __name__ == "__main__":
    w = QrcBuilder()
    w.setDirectory(os.path.join(os.path.expanduser("~"), ".ryouko-data", "profiles", "default"))
    w.start()