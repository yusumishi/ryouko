#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui

class RExtensionButton(QtGui.QToolButton):
    if sys.version_info[0] >= 3:
        javaScriptTriggered = QtCore.pyqtSignal(str)
        pythonTriggered = QtCore.pyqtSignal(str)
    else:
        javaScriptTriggered = QtCore.pyqtSignal(unicode)
        pythonTriggered = QtCore.pyqtSignal(unicode)
    linkTriggered = QtCore.pyqtSignal(QtCore.QUrl)
    def __init__(self, parent=None):
        QtGui.QToolButton.__init__(self, parent)
        self.type_ = "none"
        self.js = ""
        self.python = ""
        self.link = QtCore.QUrl("")
    def setType(self, type_):
        self.type_ = type_
    def getType(self):
        return self.type_
    def setJavaScript(self, js):
        if js.startswith("javascript:"):
            js = js.strip("javascript:").replace("%20", " ").replace("%7B", "{").replace("%7D", "}")
        self.js = js
    def setLink(self, link):
        self.link = QtCore.QUrl(link)
    def setPython(self, pie):
        self.python = pie
    def mousePressEvent(self, ev):
        if self.type_.lower() == "javascript":
            self.javaScriptTriggered.emit(self.js)
        elif self.type_.lower() == "link":
            self.linkTriggered.emit(QtCore.QUrl(self.link))
        elif self.type_.lower() == "python":
            self.pythonTriggered.emit(self.python)
        QtGui.QToolButton.mousePressEvent(self, ev)