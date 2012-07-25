#! /usr/bin/env python

import os.path, sys
from PyQt4 import QtCore, QtGui, QtWebKit
try: __file__
except: __file__ == sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)

from DialogFunctions import *
from TranslationManager import *

class RWebPage(QtWebKit.QWebPage):
    def __init__(self, parent=None):
        super(RWebPage, self).__init__()
        self.setParent(parent)
        self.userAgent = False
        self.bork = False
        self.networkAccessManager().authenticationRequired.connect(self.provideAuthentication)
    def provideAuthentication(self, reply, auth):
        if self.bork == False:
            uname = QtGui.QInputDialog.getText(None, tr('query'), tr('username'), QtGui.QLineEdit.Normal)
            if uname:
                auth.setUser(uname[0])
                pword = QtGui.QInputDialog.getText(None, tr('query'), tr('password'), QtGui.QLineEdit.Password)
                if pword:
                    auth.setPassword(pword[0])
            self.bork = True
        else:
            reply.abort()
            self.bork = False
    def userAgentForUrl(self, url):
        if self.userAgent == False:
            return QtWebKit.QWebPage.userAgentForUrl(self, url)
        else:
            if sys.version_info[0] <= 2:
                return QtCore.QString(self.userAgent)
            else:
                return str(self.userAgent)
    def setUserAgent(self, string):
        self.userAgent = string
        
    def createPlugin(self, classid, url, paramNames, paramValues):
        if classid == "ctl":
            v = QtGui.QListWidget(self.view())
            try:
                for tab in self.parent().parent().parent.closedTabsList:
                    v.addItem(tab["title"])
                v.itemClicked.connect(self.parent().parent().parent.undoCloseTabInThisTab)
            except: do_nothing()
            else:
                return v
        return
