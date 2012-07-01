#! /usr/bin/env python

from __future__ import print_function

import os.path, sys
from PyQt4 import QtCore, QtGui
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)
from DialogFunctions import *
from TranslationManager import *

class ViewSourceDialog(QtGui.QMainWindow):
    def __init__(self, reply=None, parent=None):
        super(ViewSourceDialog, self).__init__()
        self.setParent(parent)
        self.menuBar = QtGui.QMenuBar()
        self.setMenuBar(self.menuBar)

        self.text = ""
        self.findFlag = None

        self.fileMenu = QtGui.QMenu(tr("fileHKey"))
        self.menuBar.addMenu(self.fileMenu)

        self.saveAsAction = QtGui.QAction(tr("saveAs"), self)
        self.saveAsAction.setShortcut("Ctrl+S")
        self.saveAsAction.triggered.connect(self.saveAs)
        self.addAction(self.saveAsAction)
        self.fileMenu.addAction(self.saveAsAction)

        self.viewMenu = QtGui.QMenu(tr("viewHKey"))
        self.menuBar.addMenu(self.viewMenu)

        self.findAction = QtGui.QAction(tr("find"), self)
        self.findAction.setShortcut("Ctrl+F")
        self.findAction.triggered.connect(self.find)
        self.addAction(self.findAction)
        self.viewMenu.addAction(self.findAction)

        self.findNextAction = QtGui.QAction(tr("findNextHKey"), self)
        self.findNextAction.setShortcut("Ctrl+G")
        self.findNextAction.triggered.connect(self.findNext)
        self.addAction(self.findNextAction)
        self.viewMenu.addAction(self.findNextAction)

        self.findReverseAction = QtGui.QAction(tr("findReverse"), self)
        self.findReverseAction.setShortcut("Ctrl+H")
        self.findReverseAction.setCheckable(True)
        self.findReverseAction.triggered.connect(self.setFindFlag)
        self.addAction(self.findReverseAction)
        self.viewMenu.addAction(self.findReverseAction)

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

    def saveAs(self):
        fname = saveDialog(os.path.join(os.path.expanduser("~"), os.path.split(unicode(self.reply.url().toString()))[1] + ".txt"))
        if fname:
            g = unicode(self.sourceView.toPlainText())
            f = open(fname, "w")
            f.write(g)
            f.close()

    def find(self):
        find = inputDialog(tr('find'), tr('searchFor'), self.text)
        if find:
            self.text = find
        else:
            self.text = ""
        if self.findFlag:
            self.sourceView.find(self.text, self.findFlag)
        else:
            self.sourceView.find(self.text)

    def findNext(self):
        if not self.text:
            self.find()
        else:
            if self.findFlag:
                self.sourceView.find(self.text, self.findFlag)
            else:
                self.sourceView.find(self.text)

    def setFindFlag(self):
        if self.findReverseAction.isChecked():
            self.findFlag = QtGui.QTextDocument.FindBackward
        else:
            self.findFlag = None

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
