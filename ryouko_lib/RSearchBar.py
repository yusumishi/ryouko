#! /usr/bin/env python

from __future__ import division
import os.path, sys
from PyQt4 import QtCore, QtGui

try: __file__
except: __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)

from Python23Compat import *

def qMax(a, b):
    aa = float(a)
    ba = float(b)
    if aa > ba:
        return a
    else:
        return b

class RSearchBar(QtGui.QLineEdit):

    def __init__(self, icon=QtGui.QIcon(), parent=None):
        super(RSearchBar, self).__init__()
        self.setParent(parent)
        self.label = QtGui.QLabel()
        self.label.setStyleSheet("QLabel { border: 0; background: transparent; }")
        sz = self.label
        fw = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        self.s = False
        msz = self.minimumSizeHint()
        self.setMinimumSize(qMax(msz.width(), self.label.sizeHint().height() + fw * 2 + 2), qMax(msz.height(), self.label.sizeHint().height() + fw * 2 + 2))

    def paintEvent(self, ev):
        sz = self.label
        fw = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        QtGui.QLineEdit.paintEvent(self, ev)
        if unicode(self.text()) == "" and not self.hasFocus():
            self.label.render(self, QtCore.QPoint(self.rect().left() + (self.height() + 1 - sz.width())/2, (self.height() + 1 - sz.height())/2))
        if self.s == False:
            #self.setStyleSheet("QLineEdit { padding-left: %spx; }" % str(sz.width() + (self.height() + 1 - sz.width())/2))
            self.s = True
            self.redefPaintEvent()

    def redefPaintEvent(self):
        self.paintEvent = self.shortPaintEvent

    def shortPaintEvent(self, ev):
        sz = self.label
        fw = self.style().pixelMetric(QtGui.QStyle.PM_DefaultFrameWidth)
        QtGui.QLineEdit.paintEvent(self, ev)
        if unicode(self.text()) == "" and not self.hasFocus():
            self.label.render(self, QtCore.QPoint(self.rect().left() + (self.height() + 1 - sz.height())/2, (self.height() + 1 - sz.height())/2))

    def setLabel(self, text):
        self.label.setText("<i>" + unicode(text) + "</i>")
        self.label.show()
        self.label.hide()
        self.repaint()