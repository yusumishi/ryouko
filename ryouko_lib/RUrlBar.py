#! /usr/bin/env python

from __future__ import division
from PyQt4.QtCore import *
from PyQt4.QtGui import *

def qMax(a, b):
    aa = float(a)
    ba = float(b)
    if aa > ba:
        return a
    else:
        return b

class RUrlBar(QLineEdit):

    def __init__(self, icon=QIcon(), parent=None):
        super(RUrlBar, self).__init__()
        self.setParent(parent)
        self.icon = QToolButton()
        self.icon.setFixedWidth(16)
        self.icon.setFixedHeight(16)
        self.icon.setStyleSheet("QToolButton { border: 0; background: transparent; width: 16px; height: 16px; }")
        sz = self.icon
        fw = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        self.s = False
        msz = self.minimumSizeHint()
        self.setMinimumSize(qMax(msz.width(), self.icon.sizeHint().height() + fw * 2 + 2), qMax(msz.height(), self.icon.sizeHint().height() + fw * 2 + 2))

    def paintEvent(self, ev):
        sz = self.icon
        fw = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        QLineEdit.paintEvent(self, ev)
        self.icon.render(self, QPoint(self.rect().left() + (self.height() + 1 - sz.width())/2, (self.height() + 1 - sz.height())/2))
        if self.s == False:
            self.setStyleSheet("QLineEdit { padding-left: %spx; }" % str(sz.width() + (self.height() + 1 - sz.width())/2))
            self.s = True
            self.redefPaintEvent()

    def redefPaintEvent(self):
        self.paintEvent = self.shortPaintEvent

    def shortPaintEvent(self, ev):
        sz = self.icon
        fw = self.style().pixelMetric(QStyle.PM_DefaultFrameWidth)
        QLineEdit.paintEvent(self, ev)
        self.icon.render(self, QPoint(self.rect().left() + (self.height() + 1 - sz.width())/2, (self.height() + 1 - sz.height())/2))

    def setIcon(self, icon):
        self.icon.setIcon(icon)
