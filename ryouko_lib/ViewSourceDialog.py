#! /usr/bin/env python

from __future__ import print_function

from PyQt4 import QtCore, QtGui
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)
from TranslationManager import *

class ViewSourceDialog(QtGui.QMainWindow):
    def __init__(self, reply=None, parent=None):
        super(ViewSourceDialog, self).__init__()
        self.setParent(parent)
        self.sourceView = QtGui.QTextEdit()
        self.sourceView.setReadOnly(True)
        self.setCentralWidget(self.sourceView)
        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W"])
        closeWindowAction.triggered.connect(self.hide)
        self.addAction(closeWindowAction)
        self.reply = reply
        if self.reply:
            self.reply.finished.connect(self.finishRender)
        self.setWindowTitle(tr("sourceOf1") + self.reply.url().toString() + tr("sourceOf2"))
    def setReply(self, reply):
        self.reply = reply
        if self.reply:
            self.reply.finished.connect(self.finishRender)
    def closeEvent(self, ev):
        self.deleteLater()
        ev.accept()
    def finishRender(self):
        if self.reply.isFinished():
            data = self.reply.readAll()
            text = unicode(data)
            self.sourceView.setPlainText(text)
