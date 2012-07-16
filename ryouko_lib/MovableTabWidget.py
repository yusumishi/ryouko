#! /usr/bin/env python

import os.path, sys
from PyQt4 import QtCore, QtGui
try:
    filename = __file__
except:
    __file__ = sys.executable
else:
    del filename
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)
from MovableTabBar import *
from GConfFunctions import *

def doNothing():
    return

win_stylesheet = """
QTabBar::tab {
padding: 4px;
border: 1px solid palette(shadow);
}

QTabBar::tab:top {
border-top-left-radius: 4px;
border-top-right-radius:4px;
border-bottom: 1px solid palette(shadow);
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:0 palette(window), stop:1 palette(midlight));
}

QTabBar::tab:top:selected {
border-bottom: 0;
padding-bottom: 5px;
background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop:0 palette(light), stop:1 palette(window));
}
"""

class MovableTabWidget(QtGui.QTabWidget):
    def __init__(self, parent=None, forcea=False):
        super(MovableTabWidget, self).__init__(parent)
        self.parent = parent
        self.nuTabBar = MovableTabBar(self.parent)
        self.setTabBar(self.nuTabBar)
        self.setDocumentMode(True)

        theme = get_key("/desktop/gnome/shell/windows/theme")
        print(theme)

        if theme == "Ambiance":
            self.setStyleSheet(win_stylesheet)
            self.parent.setStyleSheet("""
            QMainWindow {
            background: #3C3B37;
            }
            """)

        elif theme == "Radiance":
            self.setStyleSheet(win_stylesheet)
            self.parent.setStyleSheet("""
            QMainWindow {
            background: #DFD7CF;
            }
            """)

        elif sys.platform.startswith("win"):
            self.setStyleSheet(win_stylesheet)

        self.mouseX = False
        self.mouseY = False

    def mouseDoubleClickEvent(self, e):
        e.accept()
        try:
            self.parent.newTab()
        except:
            print("MovableTabWidget could not add new tab to self.parent!")

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            try:
                doNothing()
            except:
                print("MovableTabWidget could not display its parent's context menu!")
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
