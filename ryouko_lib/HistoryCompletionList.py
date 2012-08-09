#! /usr/bin/env python

import os.path, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *

try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)

from QStringFunctions import *

class HistoryCompletionList(QListWidget):
    if sys.version_info[0] <= 2:
        statusMessage = pyqtSignal(QString)
    else:
        statusMessage = pyqtSignal(str)
    def __init__(self, parent=None):
        super(HistoryCompletionList, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.currentRowChanged.connect(self.sendStatusMessage)
    def sendStatusMessage(self, row):
        self.statusMessage.emit(self.parent.tempHistory[self.row(self.currentItem())]['url'])
    def mouseMoveEvent(self, ev):
        try: self.statusMessage.emit(qstring(self.parent.tempHistory[self.row(self.itemAt(QCursor().pos().x() - self.mapToGlobal(QPoint(0,0)).x(), QCursor().pos().y() - self.mapToGlobal(QPoint(0,0)).y()))]['url']))
        except:
            try: self.statusMessage.emit(qstring(self.parent.tempHistory[self.row(self.itemAt(QCursor().pos().x() - self.mapToGlobal(QPoint(0,0)).x(), QCursor().pos().y() - self.mapToGlobal(QPoint(0,0)).y()))]['url']))
            except:
                self.statusMessage.emit(qstring(""))


