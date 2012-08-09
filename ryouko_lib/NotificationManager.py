#! /usr/bin/env 

import os.path, sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)
app_icons = os.path.join(app_lib, 'icons')
if sys.platform.startswith("win"):
    app_logo = os.path.join(app_icons, 'about-logo.png')
else:
    app_logo = os.path.join(app_icons, "logo.svg")
from TranslationManager import *

blanktoolbarsheet = "QToolBar { border: 0; }"

class NotificationManager(QMainWindow):
    def __init__(self, parent=None):
        super(NotificationManager, self).__init__()
        if os.path.exists(app_logo):
            self.setWindowIcon(QIcon(app_logo))
        self.setWindowTitle(tr('notifications'))
        closeWindowAction = QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Ctrl+Alt+N", "Esc"])
        closeWindowAction.triggered.connect(self.hide)
        self.addAction(closeWindowAction)
        self.parent = parent
        self.toolBar = QToolBar()
        self.toolBar.setStyleSheet(blanktoolbarsheet)
        self.toolBar.setContextMenuPolicy(Qt.CustomContextMenu)
        self.toolBar.setMovable(False)
        self.clearButton = QPushButton(tr('clear'))
        self.toolBar.addWidget(self.clearButton)
        self.closeButton = QPushButton(tr('close'))
        self.closeButton.clicked.connect(self.hide)
        self.toolBar.addWidget(self.closeButton)
        self.history = QListWidget()
        self.history.setWordWrap(True)
        self.clearButton.clicked.connect(self.history.clear)
        self.setCentralWidget(self.history)
        self.addToolBar(self.toolBar)
        self.hide()

    def newNotification(self, message):
        self.history.addItem(str(self.history.count() + 1) + ": " + message)
        self.history.setCurrentRow(self.history.count() - 1)

    def center(self):
        fg = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fg.moveCenter(cp)
        self.move(fg.topLeft())

    def show(self):
        self.setVisible(True)
        self.center()
        self.activateWindow()
