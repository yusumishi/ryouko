#! /usr/bin/env python

from PyQt4.QtCore import *
from PyQt4.QtGui import *

class ContextMenu(QMenu):
    def show2(self):
        x = QPoint(QCursor.pos()).x()
        if x + self.width() > QApplication.desktop().size().width():
            x = x - self.width()
        y = QPoint(QCursor.pos()).y()
        if y + self.height() > QApplication.desktop().size().height():
            y = y - self.height()
        self.move(x, y)
        self.setVisible(True)
