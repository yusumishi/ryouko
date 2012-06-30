#! /usr/bin/env python

from PyQt4 import QtGui

class RExpander(QtGui.QLabel):
    def __init__(self, parent=None):
        super(RExpander, self).__init__()
        self.setText("")
        self.setParent(parent)
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)
