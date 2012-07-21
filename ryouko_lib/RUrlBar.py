#! /usr/bin/env python

from PyQt4 import QtCore, QtGui

def qMax(a, b):
    aa = float(a)
    ba = float(b)
    if aa > ba:
        return a
    else:
        return b

class RUrlBar(QtGui.QLineEdit):

    def __init__(self, icon=QtGui.QIcon(), parent=None):
        super(RUrlBar, self).__init__()
        self.setParent(parent)
        self.icon = QtGui.QToolButton()
        self.icon.setFixedWidth(16)
        self.icon.setFixedHeight(16)
        self.icon.setStyleSheet("QToolButton { border: 0; background: transparent; width: 16px; height: 16px; }")
        fw = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.setStyleSheet("QLineEdit { padding-left: %spx; }" % str(self.icon.sizeHint().width() + fw + 1))
        msz = self.minimumSizeHint()
        self.setMinimumSize(qMax(msz.width(), self.icon.sizeHint().height() + fw * 2 + 2), qMax(msz.height(), self.icon.sizeHint().height() + fw * 2 + 2))

    def paintEvent(self, ev):
        sz = self.icon.sizeHint()
        fw = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        QtGui.QLineEdit.paintEvent(self, ev)
        self.icon.render(self, QtCore.QPoint(self.rect().left() + (self.height() + 1 - sz.height())/2, (self.height() + 1 - sz.height())/2))

    def setIcon(self, icon):
        self.icon.setIcon(icon)
