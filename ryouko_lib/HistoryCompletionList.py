#! /usr/bin/env python

import sys
from PyQt4 import QtCore, QtGui

class HistoryCompletionList(QtGui.QListWidget):
    if sys.version_info[0] <= 2:
        statusMessage = QtCore.pyqtSignal(QtCore.QString)
    else:
        statusMessage = QtCore.pyqtSignal(str)
    def __init__(self, parent=None):
        super(HistoryCompletionList, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
        self.currentRowChanged.connect(self.sendStatusMessage)
    def sendStatusMessage(self, row):
        self.statusMessage.emit(self.parent.tempHistory[self.row(self.currentItem())]['url'])
    def mouseMoveEvent(self, ev):
        try: self.statusMessage.emit(qstring(self.parent.tempHistory[self.row(self.itemAt(QtGui.QCursor().pos().x() - self.mapToGlobal(QtCore.QPoint(0,0)).x(), QtGui.QCursor().pos().y() - self.mapToGlobal(QtCore.QPoint(0,0)).y()))]['url']))
        except:
            try: self.statusMessage.emit(qstring(self.parent.tempHistory[self.row(self.itemAt(QtGui.QCursor().pos().x() - self.mapToGlobal(QtCore.QPoint(0,0)).x(), QtGui.QCursor().pos().y() - self.mapToGlobal(QtCore.QPoint(0,0)).y()))]['url']))
            except:
                self.statusMessage.emit(qstring(""))


