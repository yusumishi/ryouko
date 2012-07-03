#! /usr/bin/env python

from PyQt4 import QtCore, QtGui

class ContextMenu(QtGui.QMenu):
    def show2(self):
        x = QtCore.QPoint(QtGui.QCursor.pos()).x()
        if x + self.width() > QtGui.QApplication.desktop().size().width():
            x = x - self.width()
        y = QtCore.QPoint(QtGui.QCursor.pos()).y()
        if y + self.height() > QtGui.QApplication.desktop().size().height():
            y = y - self.height()
        self.move(x, y)
        self.setVisible(True)
