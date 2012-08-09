#! /usr/bin/env python

import sys
from PyQt4 import QtCore

if sys.version_info[0] <= 2:
    def QString(string=""):
        return(QtCore.QString(string))
else:
    def QString(string=""):
        return(string)

if sys.version_info[0] <= 2:
    def QStringList(li=[]):
        t = QtCore.QStringList()
        for i in li:
            t.append(QString(i))
        return t
else:
    def QStringList(li=[]):
        return li

def qstring(string=""):
    return QString(string)

def qstringlist(li=[]):
    return QStringList(li)
