# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'C:\Users\DS_2\ryouko-build\ryouko_lib\mainwindow.ui'
#
# Created: Tue Feb 28 21:08:08 2012
#      by: PyQt4 UI code generator 4.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.resize(832, 480)
        MainWindow.setStyleSheet(_fromUtf8("QListWidget {\n"
"border: 0;\n"
"}"))
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralWidget = QtGui.QWidget(MainWindow)
        self.centralWidget.setObjectName(_fromUtf8("centralWidget"))
        self.mainLayout = QtGui.QGridLayout(self.centralWidget)
        self.mainLayout.setMargin(0)
        self.mainLayout.setSpacing(0)
        self.mainLayout.setObjectName(_fromUtf8("mainLayout"))
        self.progressBar = QtGui.QProgressBar(self.centralWidget)
        self.progressBar.setEnabled(True)
        self.progressBar.setStyleSheet(_fromUtf8("min-width: 200px;\n"
"max-width: 200px;"))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.mainLayout.addWidget(self.progressBar, 4, 0, 1, 1)
        self.mainToolBar = QtGui.QWidget(self.centralWidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.mainToolBar.sizePolicy().hasHeightForWidth())
        self.mainToolBar.setSizePolicy(sizePolicy)
        self.mainToolBar.setStyleSheet(_fromUtf8("#mainToolBar {\n"
"border-bottom: 1px solid palette(shadow);\n"
"}"))
        self.mainToolBar.setObjectName(_fromUtf8("mainToolBar"))
        self.mainToolBarContents = QtGui.QGridLayout(self.mainToolBar)
        self.mainToolBarContents.setMargin(0)
        self.mainToolBarContents.setSpacing(0)
        self.mainToolBarContents.setMargin(0)
        self.mainToolBarContents.setObjectName(_fromUtf8("mainToolBarContents"))
        self.mainToolBarLayout = QtGui.QHBoxLayout()
        self.mainToolBarLayout.setSpacing(0)
        self.mainToolBarLayout.setContentsMargins(-1, -1, -1, 0)
        self.mainToolBarLayout.setObjectName(_fromUtf8("mainToolBarLayout"))
        self.subToolBar = QtGui.QWidget(self.mainToolBar)
        self.subToolBar.setStyleSheet(_fromUtf8("#subToolBar {\n"
"min-width: 24px;\n"
"}\n"
"\n"
"QListWidget {\n"
"border: 0;\n"
"}\n"
"        \n"
"QToolButton, QPushButton {\n"
"min-width: 24px;\n"
"border: 1px solid transparent;\n"
"padding: 4px;\n"
"border-radius: 4px;\n"
"background-color: transparent;\n"
"}\n"
"\n"
"QToolButton:hover, QPushButton:hover {\n"
"border: 1px solid palette(shadow);\n"
"background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(light), stop:1 palette(button));\n"
"}\n"
"\n"
"QToolButton:pressed, QPushButton:pressed {\n"
"border: 1px solid palette(shadow);\n"
"background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(shadow), stop:1 palette(button));\n"
"}"))
        self.subToolBar.setObjectName(_fromUtf8("subToolBar"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.subToolBar)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.backButton = QtGui.QPushButton(self.subToolBar)
        self.backButton.setStyleSheet(_fromUtf8(""))
        self.backButton.setObjectName(_fromUtf8("backButton"))
        self.horizontalLayout.addWidget(self.backButton)
        self.nextButton = QtGui.QPushButton(self.subToolBar)
        self.nextButton.setStyleSheet(_fromUtf8(""))
        self.nextButton.setObjectName(_fromUtf8("nextButton"))
        self.horizontalLayout.addWidget(self.nextButton)
        self.stopButton = QtGui.QPushButton(self.subToolBar)
        self.stopButton.setObjectName(_fromUtf8("stopButton"))
        self.horizontalLayout.addWidget(self.stopButton)
        self.reloadButton = QtGui.QPushButton(self.subToolBar)
        self.reloadButton.setObjectName(_fromUtf8("reloadButton"))
        self.horizontalLayout.addWidget(self.reloadButton)
        self.urlBar = QtGui.QLineEdit(self.subToolBar)
        self.urlBar.setObjectName(_fromUtf8("urlBar"))
        self.horizontalLayout.addWidget(self.urlBar)
        self.goButton = QtGui.QPushButton(self.subToolBar)
        self.goButton.setStyleSheet(_fromUtf8(""))
        self.goButton.setObjectName(_fromUtf8("goButton"))
        self.horizontalLayout.addWidget(self.goButton)
        self.mainToolBarLayout.addWidget(self.subToolBar)
        self.focusURLBarButton = QtGui.QPushButton(self.mainToolBar)
        self.focusURLBarButton.setStyleSheet(_fromUtf8("max-width: 0;\n"
"min-width: 0;\n"
"width: 0;\n"
"background: transparent;"))
        self.focusURLBarButton.setText(_fromUtf8(""))
        self.focusURLBarButton.setIconSize(QtCore.QSize(0, 0))
        self.focusURLBarButton.setFlat(True)
        self.focusURLBarButton.setObjectName(_fromUtf8("focusURLBarButton"))
        self.mainToolBarLayout.addWidget(self.focusURLBarButton)
        self.searchButton = QtGui.QPushButton(self.mainToolBar)
        self.searchButton.setObjectName(_fromUtf8("searchButton"))
        self.mainToolBarLayout.addWidget(self.searchButton)
        self.mainToolBarContents.addLayout(self.mainToolBarLayout, 0, 0, 1, 1)
        self.mainLayout.addWidget(self.mainToolBar, 1, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QtGui.QApplication.translate("MainWindow", "Ryouko", None, QtGui.QApplication.UnicodeUTF8))
        self.backButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<b>Back</b><br>Alt+Left Arrow", None, QtGui.QApplication.UnicodeUTF8))
        self.backButton.setText(QtGui.QApplication.translate("MainWindow", "Back", None, QtGui.QApplication.UnicodeUTF8))
        self.backButton.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+Left", None, QtGui.QApplication.UnicodeUTF8))
        self.nextButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<b>Next</b><br>Alt+Right Arrow", None, QtGui.QApplication.UnicodeUTF8))
        self.nextButton.setText(QtGui.QApplication.translate("MainWindow", "Next", None, QtGui.QApplication.UnicodeUTF8))
        self.nextButton.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+Right", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<b>Stop</b><br>Esc", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setText(QtGui.QApplication.translate("MainWindow", "Stop", None, QtGui.QApplication.UnicodeUTF8))
        self.stopButton.setShortcut(QtGui.QApplication.translate("MainWindow", "Esc", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<b>Reload</b><br>F5", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadButton.setText(QtGui.QApplication.translate("MainWindow", "Reload", None, QtGui.QApplication.UnicodeUTF8))
        self.reloadButton.setShortcut(QtGui.QApplication.translate("MainWindow", "F5", None, QtGui.QApplication.UnicodeUTF8))
        self.urlBar.setToolTip(QtGui.QApplication.translate("MainWindow", "<b>Location Bar</b><br>Ctrl+L/Alt+D", None, QtGui.QApplication.UnicodeUTF8))
        self.goButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<b>Go</b><br>Enter", None, QtGui.QApplication.UnicodeUTF8))
        self.goButton.setText(QtGui.QApplication.translate("MainWindow", "Go", None, QtGui.QApplication.UnicodeUTF8))
        self.focusURLBarButton.setShortcut(QtGui.QApplication.translate("MainWindow", "Alt+D", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setToolTip(QtGui.QApplication.translate("MainWindow", "<b>Search</b><br>Ctrl+K", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setText(QtGui.QApplication.translate("MainWindow", "Search", None, QtGui.QApplication.UnicodeUTF8))
        self.searchButton.setShortcut(QtGui.QApplication.translate("MainWindow", "Ctrl+K", None, QtGui.QApplication.UnicodeUTF8))

