#! /usr/bin/env python

import os.path, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:
    filename = __file__
except:
    __file__ = sys.executable
else:
    del filename
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
from TranslationManager import *

class RPrintPreviewDialog(QMainWindow):
    accepted = pyqtSignal()
    def __init__(self, printer, parent=None):
        super(RPrintPreviewDialog, self).__init__()
        self.printer = printer
        self.setParent(parent)
        self.toolBar = QToolBar()
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.addToolBar(self.toolBar)
        self.printButton = QPushButton(tr("print"))
        self.printAction = QAction(self)
        self.printAction.setShortcut("Ctrl+P")
        self.printButton.clicked.connect(self.printPage)
        self.printAction.triggered.connect(self.printPage)
        self.addAction(self.printAction)
        self.toolBar.addWidget(self.printButton)
        self.previewWidget = QPrintPreviewWidget(self.printer)
        self.previewWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.previewWidget.fitToWidth()
        self.setCentralWidget(self.previewWidget)
    def show(self):
        self.setVisible(True)
        if self.parent:
            fg = self.parent().frameGeometry()
            cp = QDesktopWidget().availableGeometry().center()
            fg.moveCenter(cp)
            self.parent().move(fg.topLeft())
    def printPage(self):
        q = QPrintDialog(self.printer)
        q.open()
        q.accepted.connect(self.accepted.emit)
        q.exec_()
