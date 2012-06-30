#! /usr/bin/env python

import os.path, sys
from PyQt4 import QtCore, QtGui
try:
    filename = __file__
except:
    __file__ = sys.executable
else:
    del filename
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
from TranslationManager import *

class RPrintPreviewDialog(QtGui.QMainWindow):
    accepted = QtCore.pyqtSignal()
    def __init__(self, printer, parent=None):
        super(RPrintPreviewDialog, self).__init__()
        self.printer = printer
        self.setParent(parent)
        self.toolBar = QtGui.QToolBar()
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.addToolBar(self.toolBar)
        self.printButton = QtGui.QPushButton(tr("print"))
        self.printAction = QtGui.QAction(self)
        self.printAction.setShortcut("Ctrl+P")
        self.printButton.clicked.connect(self.printPage)
        self.printAction.triggered.connect(self.printPage)
        self.addAction(self.printAction)
        self.toolBar.addWidget(self.printButton)
        self.previewWidget = QtGui.QPrintPreviewWidget(self.printer)
        self.previewWidget.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
        self.previewWidget.fitToWidth()
        self.setCentralWidget(self.previewWidget)
    def show(self):
        self.setVisible(True)
        if self.parent:
            fg = self.parent().frameGeometry()
            cp = QtGui.QDesktopWidget().availableGeometry().center()
            fg.moveCenter(cp)
            self.parent().move(fg.topLeft())
    def printPage(self):
        q = QtGui.QPrintDialog(self.printer)
        q.open()
        q.accepted.connect(self.accepted.emit)
        q.exec_()
