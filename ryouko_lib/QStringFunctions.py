#! /usr/bin/env python

import sys
from PyQt4 import QtCore

def QString(string=""):
    if sys.version_info[0] <= 2:
        return(QtCore.QString(string))
    else:
        return(string)

def QStringList(li=[]):
    if sys.version_info[0] <= 2:
        t = QtCore.QStringList()
        for i in li:
            t.append(QString(i))
        return t
    else:
        return li

def qstring(string=""):
    return QString(string)

def qstringlist(li=[]):
    return QStringList(li)
