#! /usr/bin/env python

from PyQt4 import QtCore, QtGui

class MenuPopupWindowMenu(QtGui.QMenu):
    def __init__(self, show=None, parent=None):
        QtGui.QMenu.__init__(self, parent)
        self.show = show
        self.aboutToShow.connect(self.show)
    def setVisible(self, isVisible=True):
        QtGui.QMenu.setVisible(self, isVisible)
        QtGui.QMenu.setVisible(self, False)

class MenuPopupWindow(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(MenuPopupWindow, self).__init__(parent)
        self.parent = parent
        self.widget = QtGui.QWidget(self)
        self.setCentralWidget(self.widget)
        self.mainLayout = QtGui.QVBoxLayout()
        self.mainLayout.setContentsMargins(0,0,0,0)
        self.mainLayout.setSpacing(0)
        self.styleSheet = "QMainWindow { border: 1px solid palette(shadow);} QToolButton:focus, QPushButton:focus { background: palette(highlight); border: 1px solid palette(highlight); color: palette(highlighted-text); }"
        self.widget.setLayout(self.mainLayout)
    def layout(self):
        return self.mainLayout
    def primeDisplay(self):
        return
    def center(self):
        fg = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())
    def display(self, menu = False, x = 0, y = 0, width = 0, height = 0):
        self.primeDisplay()
        if menu == True:
            self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
            self.setStyleSheet(self.styleSheet)
            self.show()
            if x - self.width() + width < 0:
                x = 0
            else:
                x = x - self.width() + width
            if y + height + self.height() >= QtGui.QApplication.desktop().size().height():
                y = y - self.height()
            else:
                y = y + height
            self.move(x, y)
        else:
            self.setWindowFlags(QtCore.Qt.Widget)
            self.setStyleSheet("")
            self.show()
            self.center()
