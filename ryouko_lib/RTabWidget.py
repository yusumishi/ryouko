#! /usr/bin/env python

import os.path, sys
from PyQt4 import QtGui
try:
    filename = __file__
except:
    __file__ = sys.executable
else:
    del filename
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)
from RTabBar import *

class RTabWidget(QtGui.QTabWidget):
    def __init__(self, parent=None, forcea=False):
        super(RTabWidget, self).__init__(parent)
        self.parent = parent
        self.nuTabBar = RTabBar(self.parent)
        self.setTabBar(self.nuTabBar)
        self.setDocumentMode(True)
        self.mouseX = False
        self.mouseY = False

    def mouseDoubleClickEvent(self, e):
        e.accept()
        try:
            self.parent.newTab()
        except:
            print("RTabWidget could not add new tab to self.parent!")

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            try:
                self.parent.showTabsContextMenu()
            except:
                print("RTabWidget could not display its parent's context menu!")
        else:
            self.mouseX = ev.globalX()
            self.origX = self.parent.x()
            self.mouseY = ev.globalY()
            self.origY = self.parent.y()

    def mouseMoveEvent(self, ev):
        if self.mouseX and self.mouseY and not self.isMaximized():
            self.parent.move(self.origX + ev.globalX() - self.mouseX,
self.origY + ev.globalY() - self.mouseY)

    def mouseReleaseEvent(self, ev):
        self.mouseX = False
        self.mouseY = False
