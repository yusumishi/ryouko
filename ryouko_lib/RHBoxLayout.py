#! /usr/bin/env python

from PyQt4 import QtGui

class RHBoxLayout(QtGui.QHBoxLayout):
    def __init__(self, parent=None):
        super(RHBoxLayout, self).__init__()
        self.setParent(parent)
        self.setContentsMargins(0,0,0,0)
