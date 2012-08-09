#! /usr/bin/env python

import sys
from PyQt4 import QtCore

if sys.version_info[0] >= 3:
    def QString(string=""):
        return(string)
    def qstring(string=""):
        return QString(string)
else:
    def qstring(string=""):
        return QtCore.QString(string)

if sys.version_info[0] <= 2:
    def QStringList(li=[]):
        t = QtCore.QStringList()
        for i in li:
            t.append(QtCore.QString(i))
        return t
else:
    def QStringList(li=[]):
        return li

def qstringlist(li=[]):
    return QStringList(li)
