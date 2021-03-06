#! /usr/bin/env python

from __future__ import print_function

from PyQt4 import QtGui

class MovableTabBar(QtGui.QTabBar):
    def __init__(self, parent=None):
        super(MovableTabBar, self).__init__(parent)
        self.parent = parent

    def mouseDoubleClickEvent(self, e):
        e.accept()
        try:
            self.parent.newTab()
        except:
            print("MovableTabWidget could not add new tab to self.parent!")
    #def mouseDoubleClickEvent(self, e):
        #e.accept()
        #try:
            #self.parent.newTab()
            #self.parent.tabs.widget(self.parent.tabs.currentIndex()).webView.buildNewTabPage()
        #except:
            #print("", end="")
