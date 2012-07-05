#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtWebKit

class RWebPage(QtWebKit.QWebPage):
    def __init__(self, parent=None):
        super(RWebPage, self).__init__()
        self.setParent(parent)
        self.userAgent = False
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
