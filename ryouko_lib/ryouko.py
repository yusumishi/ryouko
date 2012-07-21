#! /usr/bin/env python

# This file is licensed under the terms of the following MIT License:

## START OF LICENSE ##
"""
Copyright (c) 2012 Daniel Sim (foxhead128)
Portions of the code are copyright (c) 2011 roberto.alsina

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
## END OF LICENSE ##

from __future__ import print_function
import locale

def do_nothing():
    return

try:
    from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
except:
    from Tkinter import *
    root = Tk()
    root.title(tr('error'))
    w = Label(root, text=tr('noPyQtError'))
    w.pack()
    button = Button(root, text="OK", command=sys.exit)
    button.pack()
    root.mainloop()
    sys.exit()

use_unity_launcher = False
try:
    from gi.repository import Unity, Gio, GObject, Dbusmenu
except:
    do_nothing()
else:
    use_unity_launcher = True

use_linux_notifications = False
try:
    import pynotify
except:
    do_nothing()
else:
    pynotify.init("Ryouko")
    use_linux_notifications = True

import os, sys, json, time, datetime, string, shutil
if sys.platform.startswith("linux"):
    import commands

try: from urllib.request import urlretrieve
except ImportError:
    try: from urllib import urlretrieve
    except:
        print("", end="")
    else:
        import urllib
else:
    import urllib.request

try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
app_locale = locale.getdefaultlocale()[0]
sys.path.append(app_lib)
app_google_docs_extensions = [".doc", ".pdf", ".ppt", ".pptx", ".docx", ".xls", ".xlsx", ".pages", ".ai", ".psd", ".tiff", ".dxf", ".svg", ".eps", ".ps", ".ttf", ".xps", ".zip", ".rar"]
app_default_useragent = "Mozilla/5.0 (X11, Linux x86_64) AppleWebKit/534.34 (KHTML, like Gecko) Qt/4.8.1 Safari/534.34"
app_webview_default_icon = QtGui.QIcon()

from ryouko_common import *
from Python23Compat import *
from QStringFunctions import *
from SystemTerminal import *
from SettingsManager import *
from RWebPage import *
from DownloaderThread import *
from DialogFunctions import *
from MovableTabWidget import *
from GConfFunctions import *
from BrowserHistory import *
from HistoryCompletionList import *
from BookmarksManager import *
from ContextMenu import *
from MenuPopupWindow import *
from ViewSourceDialog import *
from RExpander import *
from SearchManager import *
from RPrintPreviewDialog import *
from RHBoxLayout import *
from NotificationManager import *
from TranslationManager import *
from DownloadManager import *

app_gnome_unity_integration = False
if sys.platform.startswith("linux"):
    if "gnome-session" in commands.getoutput('ps -A'):
        app_gnome_unity_integration = True
app_use_ambiance = False
if sys.platform.startswith("linux"):
    if get_key("/desktop/gnome/shell/windows/theme") == "Ambiance" and "gnome-session" in commands.getoutput('ps -A'):
        app_use_ambiance = True

app_windows = []
app_closed_windows = []
app_info = os.path.join(app_lib, "info.txt")
app_icons = os.path.join(app_lib, 'icons')
app_version = "N/A"
app_codename = "N/A"
if os.path.exists(app_info):
    readVersionFile = open(app_info)
    metadata = readVersionFile.readlines()
    readVersionFile.close()
    if len(metadata) > 0:
        app_version = metadata[0].rstrip("\n")
        if len(metadata) > 1:
            app_codename = metadata[1].rstrip("\n")
app_gui = os.path.join(app_lib, "mainwindow.ui")
app_home = os.path.expanduser(os.path.join("~", ".ryouko-data"))
app_profile_name = "default"
app_default_profile_file = os.path.join(app_home, "profiles.txt")
app_profile_folder = os.path.join(app_home, "profiles")
app_commandline = ""
app_profile_exists = False
app_kill_cookies = False
app_kill_temp_files = False
for arg in sys.argv:
    app_commandline = "%s%s " % (app_commandline, arg)
if sys.platform.startswith("win"):
    app_logo = os.path.join(app_icons, 'about-logo.png')
else:
    app_logo = os.path.join(app_icons, "logo.svg")
user_links = ""

def loadCookies():
    if os.path.exists(app_cookies):
        global app_cookiejar
        cookieFile = open(app_cookies, "r")
        try: c = json.load(cookieFile)
        except:
            print("Error! Cookies could not be loaded!")
            c = []
        cookieFile.close()
        cookies = []
        for cookie in c:
            cookies.append(QtNetwork.QNetworkCookie().parseCookies(QtCore.QByteArray(cookie))[0])
        app_cookiejar.setAllCookies(cookies)

def saveCookies():
    if app_kill_cookies == False:
        cookieFile = open(app_cookies, "w")
        cookies = []
        if sys.version_info[0] >= 3:
            for c in app_cookiejar.allCookies():
                cookies.append(unicode(qstring(c.toRawForm())).strip("b'").rstrip("'"))
        else:
            for c in app_cookiejar.allCookies():
                cookies.append(unicode(qstring(c.toRawForm())))
        json.dump(cookies, cookieFile)
        cookieFile.close()
    else:
        if sys.platform.startswith("linux"):
            os.system("shred -v \"%s\"" % (app_cookies))
        try: os.remove(app_cookies)
        except:
            doNothing()

app_cookiejar = QtNetwork.QNetworkCookieJar(QtCore.QCoreApplication.instance())


class RSettingsManager(SettingsManager):
    def errorMessage(self, backend):
        notificationMessage("Error!", "Backend %s could not be found!" % (backend))

settingsManager = RSettingsManager()

def changeProfile(profile, init = False):
    global app_profile_name
    global app_profile
    global app_links
    global app_lock
    global app_cookies
    global app_instance2
    global app_profile_exists
    app_profile_name = os.path.split(profile)[1]
    app_profile = profile
    app_links = os.path.join(app_profile, "links")
    app_lock = os.path.join(app_profile, ".lockfile")
    app_cookies = os.path.join(app_profile, "cookies.json")
    app_instance2 = os.path.join(app_profile, "instance2-says.txt")
    loadCookies()
    migrate = False
    if not os.path.isdir(app_home):
        os.mkdir(app_home)
    else:
        migrate = False
    if not os.path.isdir(app_profile_folder):
        os.makedirs(app_profile_folder)
    if not os.path.isdir(app_profile):
        os.makedirs(app_profile)
    else:
        if init == False:
            app_profile_exists = True
    if migrate == True:
        l = os.listdir(app_home)
        for fname in l:
            fpath = os.path.join(app_home, fname)
            if not fpath == app_profile_folder:
                if not os.path.exists(os.path.join(app_profile, fname)):
                    shutil.move(fpath, app_profile)
    settingsManager.changeProfile(app_profile)
    try: bookmarksManager
    except: doNothing()
    else: bookmarksManager.setDirectory(app_links)

    try: browserHistory
    except: doNothing()
    else:
        browserHistory.setAppProfile(app_profile)
        browserHistory.reload()

    try: searchManager
    except: doNothing()
    else: searchManager.changeProfile(app_profile)

app_default_profile_name = "default"
if os.path.exists(app_default_profile_file):
    f = open(app_default_profile_file)
    app_default_profile_name = f.read()
    f.close()
    app_default_profile_name = app_default_profile_name.replace("\n", "")
if not os.path.exists(os.path.join(app_profile_folder, app_default_profile_name)):
    app_default_profile_name = "default"
changeProfile(os.path.join(app_profile_folder, app_default_profile_name), True)

reset = False

blanktoolbarsheet = "QToolBar { border: 0; }"
windowtoolbarsheet = "QToolBar { border: 0; background: palette(window); }"
dw_stylesheet = "QDockWidget { color: #dfdbd2; }"

# From http://stackoverflow.com/questions/448207/python-downloading-a-file-over-http-with-progress-bar-and-basic-authentication

def hiddenNotificationMessage(message="This is a message."):
    if use_linux_notifications == False:
        notificationManager.newNotification(message)
    else:
        linux_notification(message)

def notificationMessage(message="This is a message."):
    if use_linux_notifications == False:
        notificationManager.show()
        notificationManager.newNotification(message)
    else:
        linux_notification(message)

def linux_notification(string="This is a message."):
    n = pynotify.Notification(tr("ryoukoSays"), string)
    n.show()

def prepareQuit():
    if os.path.exists(app_lock) and not os.path.isdir(app_lock):
        os.remove(app_lock)
    saveCookies()
    try: settingsManager.settings['cloudService']
    except: doNothing()
    else:
        if settingsManager.settings['cloudService'] != "No":
            local_app_profile = os.path.join(app_profile_folder, app_profile_name)
            if os.path.exists(os.path.join(local_app_profile, "settings.json")):
                os.remove(os.path.join(local_app_profile, "settings.json"))
            try: shutil.copy(os.path.join(app_profile, "settings.json"), local_app_profile)
            except:
                doNothing()
    sys.exit()

def touch(fname):
    f = open(fname, "w")
    f.write("")
    f.close()

searchManager = SearchManager(app_profile)

class SearchEditor(MenuPopupWindow):
    def __init__(self, parent=None):
        super(SearchEditor, self).__init__(parent)
        self.parent = parent
        self.setWindowTitle(tr('searchEditor'))
        self.styleSheet = "QMainWindow { border: 1px solid palette(shadow);} QToolBar { border: 0; }"
        if os.path.exists(app_logo):
            self.setWindowIcon(QtGui.QIcon(app_logo))

        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Ctrl+Shift+K"])
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        self.entryBar = QtGui.QToolBar()
        self.entryBar.setStyleSheet(blanktoolbarsheet)
        self.entryBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.entryBar.setMovable(False)
        self.addToolBar(self.entryBar)

        eLabel = QtGui.QLabel(" " + tr('newExpression'))
        self.entryBar.addWidget(eLabel)
        self.expEntry = QtGui.QLineEdit()
        self.expEntry.returnPressed.connect(self.addSearch)
        self.entryBar.addWidget(self.expEntry)
        self.addSearchButton = QtGui.QPushButton(tr("add"))
        self.addSearchButton.clicked.connect(self.addSearch)
        self.entryBar.addWidget(self.addSearchButton)

        self.engineList = QtGui.QListWidget()
        self.engineList.currentItemChanged.connect(self.applySearch)
        self.setCentralWidget(self.engineList)

        self.takeSearchAction = QtGui.QAction(self)
        self.takeSearchAction.triggered.connect(self.takeSearch)
        self.takeSearchAction.setShortcut("Del")
        self.addAction(self.takeSearchAction)

        self.hideAction = QtGui.QAction(self)
        self.hideAction.triggered.connect(self.hide)
        self.hideAction.setShortcut("Esc")
        self.addAction(self.hideAction)

    def primeDisplay(self):
        self.reload()
        self.expEntry.setFocus()

    def focusOutEvent(self, e):
        e.accept()
        self.hide()

    def reload(self):
        self.engineList.clear()
        for name in searchManager.searchEngines:
            keyword = "None"
            if searchManager.searchEngines[name]['keyword'] != "":
                keyword = searchManager.searchEngines[name]['keyword']
            self.engineList.addItem("%s\nKeyword: %s" % (name, keyword))
        for item in range(0, self.engineList.count()):
            if searchManager.searchEngines[unicode(self.engineList.item(item).text()).split("\n")[0]]['expression'] == searchManager.currentSearch:
                self.engineList.setCurrentItem(self.engineList.item(item))
                break

    def addSearch(self):
        if "%s" in self.expEntry.text():
            name = inputDialog(tr('query'), tr('enterName'))
            if name and name != "":
                keyword = inputDialog(tr('query'), tr('enterKeyword'))
                searchManager.add(name, self.expEntry.text(), keyword)
            self.reload()
        else:
            message(tr('error'), tr('newSearchError'), "warn")

    def applySearch(self, item=False, old=False):
        if item:
            try: unicode(item.text()).split("\n")[0]
            except:
                notificationMessage(tr('searchError'))
            else:
                searchManager.change(unicode(item.text()).split("\n")[0])

    def takeSearch(self):
        searchManager.remove(unicode(self.engineList.currentItem().text()).split("\n")[0])
        self.reload()

searchEditor = None

bookmarksManager = BookmarksManager(app_links)

def rebuild_bookmarks_toolbar():
    global user_links
    user_links = reload_user_links(app_links)

bookmarksManager.bookmarksChanged.connect(rebuild_bookmarks_toolbar)

bookmarksManager.setDirectory(app_links)

class BookmarksManagerGUI(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(BookmarksManagerGUI, self).__init__()
        self.parent = parent
        if os.path.exists(app_logo):
            self.setWindowIcon(QtGui.QIcon(app_logo))
        self.setWindowTitle(tr('bookmarks'))
        self.nameToolBar = QtGui.QToolBar("Add a bookmarky")
        if app_gnome_unity_integration:
            self.nameToolBar.setStyleSheet(windowtoolbarsheet)
        else:
            self.nameToolBar.setStyleSheet(blanktoolbarsheet)
        self.nameToolBar.setMovable(False)
        self.nameToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        nameLabel = QtGui.QLabel(tr('name') + ": ")
        self.nameField = QtGui.QLineEdit()
        self.nameField.returnPressed.connect(self.addBookmark)
        self.nameToolBar.addWidget(nameLabel)
        self.nameToolBar.addWidget(self.nameField)
        self.urlToolBar = QtGui.QToolBar("Add a bookmarky")
        if app_gnome_unity_integration:
            self.urlToolBar.setStyleSheet(windowtoolbarsheet)
        else:
            self.urlToolBar.setStyleSheet(blanktoolbarsheet)
        self.urlToolBar.setMovable(False)
        self.urlToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        uLabel = QtGui.QLabel(tr('url') + ": ")
        self.urlField = QtGui.QLineEdit()
        self.urlField.returnPressed.connect(self.addBookmark)
        self.urlToolBar.addWidget(uLabel)
        self.urlToolBar.addWidget(self.urlField)
        self.finishToolBar = QtGui.QToolBar()
        if app_gnome_unity_integration:
            self.finishToolBar.setStyleSheet(windowtoolbarsheet)
        else:
            self.finishToolBar.setStyleSheet(blanktoolbarsheet)
        self.finishToolBar.setMovable(False)
        self.finishToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.addButton = QtGui.QPushButton(tr('add'))
        self.addButton.clicked.connect(self.addBookmark)
        self.finishToolBar.addWidget(self.addButton)
        self.removeButton = QtGui.QPushButton(tr('remove'))
        self.removeButton.clicked.connect(self.removeBookmark)
        self.finishToolBar.addWidget(self.removeButton)
        self.bookmarksList = QtGui.QListWidget()
        self.bookmarksList.currentRowChanged.connect(self.setText)
        self.bookmarksList.itemActivated.connect(self.openBookmark)
        removeBookmarkAction = QtGui.QAction(self)
        removeBookmarkAction.setShortcut("Del")
        removeBookmarkAction.triggered.connect(self.removeBookmark)
        self.addAction(removeBookmarkAction)
        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Ctrl+Shift+B", "Ctrl+Shift+O"])
        if self.parent:
            closeWindowAction.triggered.connect(self.parent.close)
        else:
            closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        otherTabAction = QtGui.QAction(self)
        otherTabAction.setShortcut("Ctrl+Shift+H")
        otherTabAction.triggered.connect(self.switchTabs)
        self.addAction(otherTabAction)

        bookmarksManager.bookmarksChanged.connect(self.reload_)
        self.addToolBar(self.nameToolBar)
        self.addToolBarBreak()
        self.addToolBar(self.urlToolBar)
        self.addToolBarBreak()
        self.addToolBar(self.finishToolBar)
        self.setCentralWidget(self.bookmarksList)
        self.reload_()

    def setText(self):
        if self.bookmarksList.currentItem():
            self.nameField.setText(self.bookmarksList.currentItem().text())
            for bookmark in bookmarksManager.bookmarks:
                if bookmark["name"] == unicode(self.bookmarksList.currentItem().text()):
                    self.urlField.setText(bookmark["url"])

    def switchTabs(self):
        if self.parent.tabs:
            self.parent.tabs.setCurrentIndex(1)

    def display(self):
        if self.parent.display and self.parent.tabs:
            self.parent.display()
            self.parent.tabs.setCurrentIndex(0)
            self.show()
            self.nameField.setFocus()
            self.nameField.selectAll()
            self.activateWindow()
        else:
            self.show()
            self.resize(640, 480)
            self.nameField.setFocus()
            self.nameField.selectAll()
            self.activateWindow()
    def reload_(self):
        self.bookmarksList.clear()
        for bookmark in bookmarksManager.bookmarks:
            self.bookmarksList.addItem(bookmark["name"])
    def openBookmark(self):
        if win.closed:
            win.show()
            win.closed = False
            win.resize(800, 480)
        for bookmark in bookmarksManager.bookmarks:
            if bookmark["name"] == unicode(self.bookmarksList.currentItem().text()):
                win.newTab(bookmark["url"])
                break
    def addBookmark(self):
        if unicode(self.nameField.text()) != "" and unicode(self.urlField.text()) != "":
            bookmarksManager.add(unicode(self.urlField.text()), unicode(self.nameField.text()))
        else:
            notificationMessage(tr('bookmarkError'))
    def removeBookmarkIfFocused(self):
        if self.bookmarksList.hasFocus():
            removeBookmark()
    def removeBookmark(self):
        bookmarksManager.removeByName(unicode(self.bookmarksList.currentItem().text()))
    def closeEvent(self, ev):
        try:
            self.parent.close()
        except:
            doNothing()
        return QtGui.QMainWindow.closeEvent(self, ev)

class ClearHistoryDialog(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(ClearHistoryDialog, self).__init__()
        self.parent = parent

        self.setWindowModality(QtCore.Qt.ApplicationModal)

        self.setWindowTitle(tr('clearHistory'))
        if os.path.exists(app_logo):
            self.setWindowIcon(QtGui.QIcon(app_logo))

        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Esc", "Ctrl+W", "Ctrl+Shift+Del"])
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        self.contents = QtGui.QWidget()
        self.layout = QtGui.QVBoxLayout()
        self.contents.setLayout(self.layout)
        self.setCentralWidget(self.contents)
        self.createClearHistoryToolBar()

    def show(self):
        self.setVisible(True)
        centerWidget(self)

    def display(self):
        self.show()
        self.activateWindow()

    def createClearHistoryToolBar(self):
        label = QtGui.QLabel(tr("clearHistoryDesc") + ":")
        self.layout.addWidget(label)
        self.selectRange = QtGui.QComboBox()
        self.selectRange.addItem(tr('lastMin'))
        self.selectRange.addItem(tr('last2Min'))
        self.selectRange.addItem(tr('last5Min'))
        self.selectRange.addItem(tr('last10Min'))
        self.selectRange.addItem(tr('last15Min'))
        self.selectRange.addItem(tr('last30Min'))
        self.selectRange.addItem(tr('lastHr'))
        self.selectRange.addItem(tr('last2Hr'))
        self.selectRange.addItem(tr('last4Hr'))
        self.selectRange.addItem(tr('last8Hr'))
        self.selectRange.addItem(tr('last24Hr'))
        self.selectRange.addItem(tr('today'))
        self.selectRange.addItem(tr('everything'))
        self.selectRange.addItem("----------------")
        self.selectRange.addItem(tr('cookies'))
        self.selectRange.addItem(tr('localStorage'))
        self.layout.addWidget(self.selectRange)
        self.toolBar = QtGui.QToolBar("")
        self.toolBar.setStyleSheet(blanktoolbarsheet)
        self.toolBar.setMovable(False)
        self.toolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolBar)
        self.clearHistoryButton = QtGui.QPushButton(tr('clear'))
        self.clearHistoryButton.clicked.connect(self.clearHistory)
        self.toolBar.addWidget(self.clearHistoryButton)
        self.closeButton = QtGui.QPushButton(tr('close'))
        self.closeButton.clicked.connect(self.close)
        self.toolBar.addWidget(self.closeButton)

    def clearHistoryRange(self, timeRange=0.0):
        question = QtGui.QMessageBox.question(None, tr("warning"),
        tr("clearHistoryWarn"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if question == QtGui.QMessageBox.Yes:
            if sys.platform.startswith("linux"):
                os.system("shred -v \"%s\"" % (os.path.join(app_profile, "WebpageIcons.db")))
            try: os.remove(os.path.join(app_profile, "WebpageIcons.db"))
            except:
                doNothing()
            saveTime = time.time()
            for item in browserHistory.history:
                try:
                    difference = saveTime - int(item['time'])
                except:
                    browserHistory.reset()
                    break
                if difference <= timeRange:
                    del browserHistory.history[browserHistory.history.index(item)]
            browserHistory.save()
            for win in app_windows:
                try:
                    win.reloadHistory()
                except:
                    doNothing()
            if library.advancedHistoryViewGUI.reload_:
                library.advancedHistoryViewGUI.reload_()

    def clearHistory(self):
        if self.selectRange.currentIndex() == 0:
            self.clearHistoryRange(60.0)
        elif self.selectRange.currentIndex() == 1:
            self.clearHistoryRange(120.0)
        elif self.selectRange.currentIndex() == 2:
            self.clearHistoryRange(300.0)
        elif self.selectRange.currentIndex() == 3:
            self.clearHistoryRange(600.0)
        elif self.selectRange.currentIndex() == 4:
            self.clearHistoryRange(900.0)
        elif self.selectRange.currentIndex() == 5:
            self.clearHistoryRange(1800.0)
        elif self.selectRange.currentIndex() == 6:
            self.clearHistoryRange(3600.0)
        elif self.selectRange.currentIndex() == 7:
            self.clearHistoryRange(7200.0)
        elif self.selectRange.currentIndex() == 8:
            self.clearHistoryRange(14400.0)
        elif self.selectRange.currentIndex() == 9:
            self.clearHistoryRange(28800.0)
        elif self.selectRange.currentIndex() == 10:
            self.clearHistoryRange(86400.0)
        elif self.selectRange.currentIndex() == 11:
            question = QtGui.QMessageBox.question(None, tr("warning"),
            tr("clearHistoryWarn"), QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if question == QtGui.QMessageBox.Yes:
                if sys.platform.startswith("linux"):
                    os.system("shred -v \"%s\"" % (os.path.join(app_profile, "WebpageIcons.db")))
                try: os.remove(os.path.join(app_profile, "WebpageIcons.db"))
                except:
                    doNothing()
                saveMonth = time.strftime("%m")
                saveDay = time.strftime("%d")
                now = datetime.datetime.now()
                saveYear = "%d" % now.year
                for item in browserHistory.history:
                    if item['month'] == saveMonth and item['monthday'] == saveDay and item['year'] == saveYear:
                        del browserHistory.history[browserHistory.history.index(item)]
                browserHistory.save()
                for win in app_windows:
                    try:
                        win.reloadHistory()
                    except:
                        doNothing()
                if library.advancedHistoryViewGUI.reload_:
                    library.advancedHistoryViewGUI.reload_()
        elif self.selectRange.currentIndex() == 12:
            question = QtGui.QMessageBox.question(None, tr("warning"),
            tr("clearHistoryWarn"), QtGui.QMessageBox.Yes | 
            QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if question == QtGui.QMessageBox.Yes:
                if sys.platform.startswith("linux"):
                    os.system("shred -v \"%s\"" % (os.path.join(app_profile, "WebpageIcons.db")))
                try: os.remove(os.path.join(app_profile, "WebpageIcons.db"))
                except:
                    doNothing()
                browserHistory.history = []
                browserHistory.save()
                for win in app_windows:
                    try:
                        win.reloadHistory()
                    except:
                        doNothing()
                if library.advancedHistoryViewGUI.reload_:
                    library.advancedHistoryViewGUI.reload_()
        elif self.selectRange.currentIndex() == 14:
            question = QtGui.QMessageBox.question(None, tr("warning"),
        tr("clearHistoryWarn"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if question == QtGui.QMessageBox.Yes:
                global app_kill_cookies
                app_kill_cookies = True
                notificationMessage(tr('clearCookiesMsg'))
        elif self.selectRange.currentIndex() == 15:
            question = QtGui.QMessageBox.question(None, tr("warning"),
        tr("clearHistoryWarn"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if question == QtGui.QMessageBox.Yes:
                d = os.path.join(app_profile, "LocalStorage")
                if sys.platform.startswith("linux"):
                    os.chdir(d)
                    os.system("find \"" + d + "\" -type f -exec shred {} \;")
                try: shutil.rmtree(d)
                except:
                    doNothing()

clearHistoryDialog = None

class AdvancedHistoryViewGUI(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(AdvancedHistoryViewGUI, self).__init__()
        self.parent = parent

        self.historyToolBar = QtGui.QToolBar("")
        if app_gnome_unity_integration:
            self.historyToolBar.setStyleSheet(windowtoolbarsheet)
        else:
            self.historyToolBar.setStyleSheet(blanktoolbarsheet)
        self.historyToolBar.setMovable(False)
        self.historyToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.addToolBar(self.historyToolBar)

        clearHistoryAction = QtGui.QAction(QtGui.QIcon.fromTheme("edit-clear", QtGui.QIcon(os.path.join(app_icons, "clear.png"))), tr('clearHistoryHKey'), self)
        clearHistoryAction.setToolTip(tr('clearHistoryTT'))
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(clearHistoryDialog.show)
        self.historyToolBar.addAction(clearHistoryAction)

        self.historyToolBar.addSeparator()

        searchLabel = QtGui.QLabel(tr("searchLabel") + ": ")
        self.historyToolBar.addWidget(searchLabel)

        self.searchBox = QtGui.QLineEdit()
        self.searchBox.textChanged.connect(self.searchHistoryFromBox)
        self.historyToolBar.addWidget(self.searchBox)

        findAction = QtGui.QAction(self)
        findAction.setShortcuts(["Ctrl+F", "Ctrl+K"])
        findAction.triggered.connect(self.searchBox.setFocus)
        findAction.triggered.connect(self.searchBox.selectAll)
        self.addAction(findAction)

        self.historyView = QtGui.QTreeWidget()
        self.historyView.setHeaderLabels([tr("title"), tr("count"), tr("weekday"), tr("date"), tr("time"), tr('url')])
        self.historyView.itemActivated.connect(self.loadHistoryItem)
        self.historyView.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.setCentralWidget(self.historyView)

        deleteHistoryItemAction = QtGui.QAction(tr("delete"), self)
        deleteHistoryItemAction.setShortcut("Del")
        deleteHistoryItemAction.triggered.connect(self.deleteHistoryItem)
        self.addAction(deleteHistoryItemAction)

        self.historyViewMenu = ContextMenu()
        self.historyView.customContextMenuRequested.connect(self.historyViewMenu.show2)
        self.historyViewMenu.addAction(deleteHistoryItemAction)

        otherTabAction = QtGui.QAction(self)
        otherTabAction.setShortcuts(["Ctrl+Shift+B", "Ctrl+Shift+O"])
        otherTabAction.triggered.connect(self.switchTabs)
        self.addAction(otherTabAction)

        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Ctrl+Shift+H"])
        if self.parent:
            closeWindowAction.triggered.connect(self.parent.close)
        else:
            closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        browserHistory.historyChanged.connect(self.reload_)

        self.reload_()

    def deleteHistoryItem(self):
        if self.historyView.hasFocus():
            u = ""
            item = self.historyView.currentItem()
            if sys.version_info[0] <= 2:
                u = unicode(item.data(5, 0).toString())
            else:
                u = unicode(item.data(5, 0))
            browserHistory.removeByUrl(u)

    def searchHistoryFromBox(self):
        if self.searchBox.text() != "":
            self.searchHistory(self.searchBox.text())
        else:
            self.reload_()

    def searchHistory(self, string=""):
        string = unicode(string)
        if string != "":
            self.searchOn = True
            self.historyView.clear()
            history = []
            string = unicode(string)
            for item in browserHistory.history:
                add = False
                for subitem in item:
                    if string.lower() in unicode(item[subitem]).lower():
                        add = True
                        break
                if add == True:
                    history.append(item)
            for item in history:
                t = self.buildItem(item)
                self.historyView.addTopLevelItem(t)
        else:
            self.searchOn = False
            self.reloadHistory()

    def loadHistoryItem(self, item):
        u = ""
        if sys.version_info[0] <= 2:
            u = unicode(item.data(5, 0).toString())
        else:
            u = unicode(item.data(5, 0))
        if win.closed:
            win.show()
            win.closed = False
            win.resize(800, 480)
        win.newTab(u)

    def switchTabs(self):
        if self.parent.tabs:
            self.parent.tabs.setCurrentIndex(0)

    def clear(self):
        self.historyView.clear()

    def closeEvent(self, ev):
        try:
            self.parent.close()
        except:
            doNothing()
        return QtGui.QMainWindow.closeEvent(self, ev)
    
    def display(self):
        if self.parent.display and self.parent.tabs:
            self.parent.display()
            self.parent.tabs.setCurrentIndex(1)
            self.show()
            self.searchBox.setFocus()
            self.searchBox.selectAll()
            self.activateWindow()
        else:
            self.show()
            self.resize(640, 480)
            self.searchBox.setFocus()
            self.searchBox.selectAll()
            self.activateWindow()

    def buildItem(self, item):
        t = QtGui.QTreeWidgetItem(qstringlist([item['name'], str(item['count']), item['weekday'], str(item['year']) + "/" + str(item['month']) + "/" + str(item['monthday']), item['timestamp'], item['url']]))
        return t

    def reload_(self):
        self.historyView.clear()
        for item in browserHistory.history:
            t = self.buildItem(item)
            self.historyView.addTopLevelItem(t)

class Library(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(Library, self).__init__()
        self.parent = parent
        if os.path.exists(app_logo):
            self.setWindowIcon(QtGui.QIcon(app_logo))

        self.setWindowTitle(tr('library'))
        self.tabs = MovableTabWidget(self, True)
        self.setCentralWidget(self.tabs)
        self.bookmarksManagerGUI = BookmarksManagerGUI(self)
        self.tabs.addTab(self.bookmarksManagerGUI, tr('bookmarks'))
        self.advancedHistoryViewGUI = AdvancedHistoryViewGUI(self)
        self.tabs.addTab(self.advancedHistoryViewGUI, tr('historyHKey'))
    def display(self):
        self.show()
        self.resize(640, 480)
        self.activateWindow()

library = ""

browserHistory = BrowserHistory(app_profile)

def runThroughFilters(url):
    remove = False
    invert = False
    for f in settingsManager.filters:
        exception = f.startswith("@@")
        ending = f.endswith("|")
        beginning = f.startswith("||")
        if exception:
            f = f.strip("@@")
            invert = True
        if beginning:
            f = f.strip("||")
            if sys.version_info[0] < 3:
                string.split(f, "://")
            else:
                f.split("://")
            if url.startswith(f):
                remove = True
                if invert == True:
                    remove = False
                else:
                    break
        if ending:
            f = f.rstrip("|")
            if url.endswith(f):
                remove = True
                if invert == True:
                    remove = False
                else:
                    break
        if sys.version_info[0] < 3:
            g = string.split(f, "*")
        else:
            g = f.split("*")
        h = 0
        for word in g:
            if not word in url:
                remove = False
            else:
                h += 1
        if h >= len(g):
            remove = True
            if invert == True:
                remove = False
            else:
                break
    return remove

def showAboutPage(webView):
    webView.load(QtCore.QUrl("about:blank"))
    webView.setHtml("""<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01//EN"
        "http://www.w3.org/TR/html4/strict.dtd">
        <html style='padding-bottom: 19.25pt;'>
        <head>
        <title>""" + tr('aboutRyouko') + """</title>
        <script type='text/javascript'>
        window.onload = function() {
            document.getElementById(\"userAgent\").innerHTML = navigator.userAgent;
        }
        </script>
        <style type="text/css">
        b, h1, h2 {
        font-family: sans-serif;
        }

        *:not(b):not(h1):not(h2) {
        font-family: monospace;
        }

        #toolbar {
        overflow-y: auto;
        height: 19.25pt;
        width: 100%;
        left: 0;
        bottom: 0;
        padding: 2px;
        padding-left: 0;
        padding-right:0;
        background: ThreeDFace;
        position: fixed;
        visibility: visible;
        z-index: 9001;
        border-top: 1px solid ThreeDShadow;
        }

        #toolbar * {
        font-family: sans-serif;
        font-size: 11pt;
        background: transparent;
        padding: 0;
        border: 0;
        color: ButtonText;
        text-decoration: none;
        -webkit-appearance: none;
        }

        #toolbar a:hover,
        #ryouko-toolbar input:hover {
        text-decoration: underline;
        }
        </style>
        </head>
        <body style='font-family: sans-serif; font-size: 11pt;'>
        <span id='toolbar'><a style='font-family: sans-serif;' href='#about'>""" + tr('aboutRyouko') + """</a> <a style='font-family: sans-serif;' href='#licensing'>""" + tr('license') + """</a></span>
        <center>
        <div style=\"max-width: 640px;\">
        <a name='about'></a>
        <h1 style='margin-bottom: 0;'>""" + tr('aboutRyouko') + """</h1>
        <img src='file://%""" + os.path.join(app_icons, "about-logo.png") + """'></img><br/>
        <div style=\"text-align: left;\">
        <b>Ryouko:</b> """ + app_version + """<br/>
        <b>""" + tr('codename') + """:</b> \"""" + app_codename + """\"<br/>
        <b>OS:</b> """ + sys.platform + """<br/>
        <b>Qt:</b> """ + str(QtCore.qVersion()) + """<br/>
        <b>Python:</b> """ + str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2]) + """<br/>
        <b>""" + tr("userAgent") + """:</b> <span id="userAgent">JavaScript must be enabled to display the user agent!</span><br/>
        <b>""" + tr("commandLine") + """:</b> """ + app_commandline + "<br/>\
        <b>" + tr('executablePath') + ":</b> " + os.path.realpath(__file__) + "<br/><center>\
        <a name='licensing'></a>\
        <h1>" + tr('license') + "</h1>\
        <iframe style='border: 0; width: 100%; height: 640px;' src='file://%" + os.path.join(app_lib, "LICENSE.txt") + "'></iframe></center></div></div></center></body></html>")

class RAboutDialog(QtWebKit.QWebView):
    def __init__(self, parent=None):
        super(RAboutDialog, self).__init__()
        self.parent = parent
        page = RWebPage()
        self.setPage(page)
        if os.path.exists(app_logo):
            self.setWindowIcon(QtGui.QIcon(app_logo))
#        self.setWindowModality(QtCore.Qt.ApplicationModal)
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.closeWindowAction = QtGui.QAction(self)
        self.closeWindowAction.setShortcuts(["Ctrl+W", "Esc", "Enter"])
        self.closeWindowAction.triggered.connect(self.close)
        self.addAction(self.closeWindowAction)
        self.setWindowTitle(tr('aboutRyouko'))
        showAboutPage(self)
    def updateUserAgent(self):
        try: settingsManager.settings['customUserAgent']
        except:
            doNothing()
        else:
            if settingsManager.settings['customUserAgent'].replace(" ", "") != "":
                self.page().userAgent = settingsManager.settings['customUserAgent']
            else:
                self.page().userAgent = app_default_useragent
        showAboutPage(self)
    def show(self):
        self.setVisible(True)
        centerWidget(self)

aboutDialog = None

downloadManagerGUI = None

def downloadStarted():
    global downloadStartTimer
    notificationMessage(tr('downloadStarted'))
    downloadStartTimer.stop()

downloadStartTimer = QtCore.QTimer()
downloadStartTimer.timeout.connect(downloadStarted)

def downloadFinished():
    notificationMessage(tr('downloadFinished'))

notificationManager = None

class RWebView(QtWebKit.QWebView):
    createNewWindow = QtCore.pyqtSignal(QtWebKit.QWebPage.WebWindowType)
    def __init__(self, parent=False, pb=False):
        super(RWebView, self).__init__()
        self.parent = parent
        page = RWebPage(self)
        self.setPage(page)
        self.destinations = []
        self.sourceViews = []
        self.autoSaveInterval = 0
        self.urlChanged.connect(self.autoSave)
        self.printer = None
        self.replies = []
        self.newWindows = [0]
        self.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
        if os.path.exists(app_logo):
            self.setWindowIcon(QtGui.QIcon(app_logo))
        if pb:
            self.setWindowTitle("Ryouko (PB)")
        else:
            self.setWindowTitle("Ryouko")
        if parent == False:
            self.parent = None
        self.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Expanding)

        self.text = ""
        self.zoomFactor = 1.0

        self.titleChanged.connect(self.updateTitle)

        self.viewSourceAction = QtGui.QAction(self)
        self.viewSourceAction.setShortcut("Ctrl+Alt+U")
        self.viewSourceAction.triggered.connect(self.viewSource)
        self.addAction(self.viewSourceAction)

        self.buildNewTabPageAction = QtGui.QAction(self)
        self.buildNewTabPageAction.setShortcut("F1")
        self.buildNewTabPageAction.triggered.connect(self.buildNewTabPage)
        self.addAction(self.buildNewTabPageAction)

        self.newWindowAction = QtGui.QAction(self)
        self.newWindowAction.triggered.connect(self.newWindow)
        self.addAction(self.newWindowAction)

        self.closeWindowAction = QtGui.QAction(self)
        self.closeWindowAction.triggered.connect(self.close)
        self.addAction(self.closeWindowAction)
        
        self.backAction = QtGui.QAction(self)
        self.backAction.setShortcut("Alt+Left")
        self.backAction.triggered.connect(self.back)
        self.addAction(self.backAction)

        self.savePageAction = QtGui.QAction(self)
        self.savePageAction.triggered.connect(self.savePage)
        self.addAction(self.savePageAction)

        self.printPageAction = QtGui.QAction(self)
        self.printPageAction.triggered.connect(self.printPreview)
        self.addAction(self.printPageAction)

        self.nextAction = QtGui.QAction(self)
        self.nextAction.setShortcut("Alt+Right")
        self.nextAction.triggered.connect(self.forward)
        self.addAction(self.nextAction)

        self.stopAction = QtGui.QAction(self)
        self.stopAction.triggered.connect(self.stop)
        self.addAction(self.stopAction)

        self.reloadAction = QtGui.QAction(self)
        self.reloadAction.triggered.connect(self.reload)
        self.reloadAction.setShortcuts(["Ctrl+R", "F5"])
        self.addAction(self.reloadAction)

        self.locationEditAction = QtGui.QAction(self)
        self.locationEditAction.triggered.connect(self.locationEdit)
        self.addAction(self.locationEditAction)

        self.findAction = QtGui.QAction(self)
        self.findAction.triggered.connect(self.find)
        self.findAction.setShortcut("Ctrl+F")
        self.addAction(self.findAction)

        self.findNextAction = QtGui.QAction(self)
        self.findNextAction.triggered.connect(self.findNext)
        self.findNextAction.setShortcuts(["Ctrl+G", "F3"])
        self.addAction(self.findNextAction)

        self.zoomInAction = QtGui.QAction(self)
        self.zoomInAction.triggered.connect(self.zoomIn)
        self.addAction(self.zoomInAction)

        self.zoomOutAction = QtGui.QAction(self)
        self.zoomOutAction.triggered.connect(self.zoomOut)
        self.addAction(self.zoomOutAction)

        self.zoomResetAction = QtGui.QAction(self)
        self.zoomResetAction.triggered.connect(self.zoomReset)
        self.addAction(self.zoomResetAction)

        self.undoCloseWindowAction = QtGui.QAction(tr('undoCloseWindow'), self)
        self.undoCloseWindowAction.triggered.connect(undoCloseWindow)
        self.addAction(self.undoCloseWindowAction)

        self.page().action(QtWebKit.QWebPage.InspectElement).setShortcut("F12")
        self.page().action(QtWebKit.QWebPage.InspectElement).triggered.connect(self.showInspector)
        self.addAction(self.page().action(QtWebKit.QWebPage.InspectElement))

        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.downloadUnsupportedContent)
        self.page().downloadRequested.connect(self.downloadFile)
        self.loadFinished.connect(self.checkForAds)
        if sys.platform.startswith("win"):
            self.loadFinished.connect(self.replaceAV)
        self.updateSettings()
        self.establishPBMode(pb)
        self.loadFinished.connect(self.loadLinks)
        if (unicode(self.url().toString()) == "about:blank" or unicode(self.url().toString()) == ""):
            self.buildNewTabPage()
            if not type(self.parent) == Browser:
                self.loadControls()
            self.updateTitle()
        if not type(self.parent) == Browser:
            self.isWindow = True
            global app_windows
            app_windows.append(self)
        else:
            self.isWindow = False

    def replaceAV(self):
        av = self.page().mainFrame().findAllElements("audio, video")
        if not os.path.exists(os.path.join(app_profile, "win-vlc.conf")) and len(av) > 0:
            q = QtGui.QMessageBox.question(None, tr("ryoukoSays"),
        tr("audioVideoUnsupported"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if q == QtGui.QMessageBox.Yes:
                wv = self.createWindow(QtWebKit.QWebPage.WebBrowserWindow)
                wv.load(QtCore.QUrl("http://www.videolan.org/vlc/index.html"))
            f = open(os.path.join(app_profile, "win-vlc.conf"), "w")
            f.write("This file is here to tell Ryouko not to ask the user to install VLC again.")
            f.close()
        for element in av:
            a = element.attributeNames()
            e = "<embed "
            for attribute in a:
                e = e + unicode(attribute) + "=\"" + unicode(element.attribute(attribute)) + "\" "
            e = e + "></embed>"
            element.replace(e)

    def translate(self):
        l = app_locale[0] + app_locale[1]
        self.load(QtCore.QUrl("http://translate.google.com/translate?hl=" + l + "&sl=auto&tl=" + l + "&u=" + unicode(self.url().toString())))

    def autoSave(self):
        self.autoSaveInterval += 1
        if self.autoSaveInterval >= 4:
            saveCookies()
            self.autoSaveInterval = 0

    def closeEvent(self, ev):
        if self.isWindow == True:
            global app_windows
            if self in app_windows:
                del app_windows[app_windows.index(self)]
            global app_closed_windows
            app_closed_windows.append(self)
        return QtGui.QMainWindow.closeEvent(self, ev)

    def showInspector(self):
        if self.parent.webInspectorDock:
            self.parent.webInspectorDock.show()
        if self.parent.webInspector:
            self.parent.webInspector.show()

    def enableControls(self):
        self.loadFinished.connect(self.loadControls)

    def loadLinks(self):
        if os.path.isdir(app_links) and not user_links == "":
            if self.page().mainFrame().findFirstElement("#ryouko-toolbar").isNull() == True:
                self.buildToolBar()
            if self.page().mainFrame().findFirstElement("#ryouko-link-bar").isNull():
                self.page().mainFrame().findFirstElement("#ryouko-link-bar-container").appendInside("<span id=\"ryouko-link-bar\"></span>")
                if not user_links == "":
                    self.page().mainFrame().findFirstElement("#ryouko-link-bar").appendInside(user_links)
                else:
                    self.evaluateJavaScript("link = document.createElement('a');\nlink.innerHTML = '%s';\ndocument.getElementById('ryouko-link-bar').appendChild(link);" % (tr("noExtensions")))

    def buildToolBar(self):
        if self.page().mainFrame().findFirstElement("#ryouko-toolbar").isNull() == True:
            self.page().mainFrame().findFirstElement("body").appendInside("""<style type="text/css">html{padding-bottom: 19.25pt;}#ryouko-toolbar {overflow-y: auto; height: 19.25pt; width: 100%; left: 0;padding: 2px;padding-left: 0;padding-right:0;background: ThreeDFace;position: fixed;visibility: visible;z-index: 9001;}#ryouko-toolbar *{font-family: sans-serif; font-size: 11pt; background: transparent; padding: 0; border: 0; color: ButtonText; text-decoration: none; -webkit-appearance: none;} #ryouko-toolbar a:hover, #ryouko-toolbar input:hover{text-decoration: underline; }</style><span id='ryouko-toolbar' style='bottom: 0; border-top: 1px solid ThreeDShadow;'><span id='ryouko-browser-controls'></span><span id='ryouko-link-bar-container'></span><input id='ryouko-switch-button' style='float: right; padding-left: 4px; padding-right: 4px; outline: 1px outset ThreeDHighlight;' value='^' type='button' onclick="if (document.getElementById('ryouko-toolbar').getAttribute('style')=='top: 0; border-bottom: 1px solid ThreeDShadow;') { document.getElementById('ryouko-toolbar').setAttribute('style', 'bottom: 0; border-top: 1px solid ThreeDShadow;'); document.getElementsByTagName('html')[0].setAttribute('style', 'padding-top: 0; padding-bottom: 19.25pt;'); document.getElementById('ryouko-switch-button').setAttribute('value','^'); } else { document.getElementById('ryouko-toolbar').setAttribute('style', 'top: 0; border-bottom: 1px solid ThreeDShadow;'); document.getElementsByTagName('html')[0].setAttribute('style', 'padding-top: 19.25pt; padding-bottom: 0;'); document.getElementById('ryouko-switch-button').setAttribute('value','v'); }"></input></span>""")

    def loadControls(self):
        if self.page().mainFrame().findFirstElement("#ryouko-toolbar").isNull() == True:
            self.buildToolBar()
        if self.page().mainFrame().findFirstElement("#ryouko-url-edit").isNull():
            self.page().mainFrame().findFirstElement("#ryouko-browser-controls").appendInside("""<input type='button' value='""" + tr('back') + """' onclick='history.go(-1);'></input><input type='button' value='""" + tr('next') + """' onclick='history.go(+1);'></input><input id='ryouko-url-edit' type='button' value='""" + tr('open') + """' onclick="url = prompt('You are currently at:\\n' + window.location.href + '\\n\\nEnter a URL here:', 'http://'); if (url != null && url != '') {if (url.indexOf('://') == -1) {url = 'http://' + url;}window.location.href = url; }");
ryoukoBrowserControls.appendChild(ryoukoURLEdit);"></input> <a href="about:blank" target="_blank">""" + tr('newWindow') + """</a><span style='margin: -2px; padding-left: 6px; padding-right: 6px;'><span style='border-right: 1px solid ThreeDShadow;'></span></span>""")

    def evaluateJavaScript(self, script):
        self.page().mainFrame().evaluateJavaScript(script)

    def checkForAds(self):
        if settingsManager.settings['adBlock']:
            elements = self.page().mainFrame().findAllElements("iframe, frame, object, embed, .ego_unit").toList()
            for element in elements:
                for attribute in element.attributeNames():
                    e = unicode(element.attribute(attribute))
                    delete = runThroughFilters(e)
                    if delete:
                        element.removeFromDocument()
                        break

    def establishPBMode(self, pb):
        self.pb = pb
        if not pb or pb == None:
            self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, True)
        else:
            self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, False)
        if not pb:
            try:
                self.page().networkAccessManager().setCookieJar(app_cookiejar)
                app_cookiejar.setParent(QtCore.QCoreApplication.instance())
            except:
                doNothing()
        else:
            cookies = QtNetwork.QNetworkCookieJar(None)
            cookies.setAllCookies([])
            self.page().networkAccessManager().setCookieJar(cookies)
        if (unicode(self.url().toString()) == "about:blank" or unicode(self.url().toString()) == "") and self.pb != None and self.pb != False:
            self.buildNewTabPage()

    def updateSettings(self):
        try: settingsManager.settings['loadImages']
        except: 
            print("", end = "")
        else:
            self.settings().setAttribute(QtWebKit.QWebSettings.AutoLoadImages, settingsManager.settings['loadImages'])
        try: settingsManager.settings['jsEnabled']
        except: 
            print("", end = "")
        else:
            self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, settingsManager.settings['jsEnabled'])
        try: settingsManager.settings['customUserAgent']
        except:
            doNothing()
        else:
            if settingsManager.settings['customUserAgent'].replace(" ", "") != "":
                self.page().setUserAgent(settingsManager.settings['customUserAgent'])
            else:
                self.page().setUserAgent(app_default_useragent)
        try: settingsManager.settings['storageEnabled']
        except:
            self.settings().enablePersistentStorage(qstring(app_profile))
        else:
            if settingsManager.settings['storageEnabled'] == True:
                self.settings().enablePersistentStorage(qstring(app_profile))
            else:
                self.settings().setOfflineStoragePath(qstring(""))
                self.settings().setLocalStoragePath(qstring(""))
                self.settings().setOfflineWebApplicationCachePath(qstring(""))
                self.settings().setIconDatabasePath(qstring(app_profile))
        try: settingsManager.settings['pluginsEnabled']
        except: 
            print("", end = "")
        else:
            self.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, settingsManager.settings['pluginsEnabled'])
        try: settingsManager.settings['privateBrowsing']
        except: 
            print("", end = "")
        else:
            self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, settingsManager.settings['privateBrowsing'])
            if settingsManager.settings['privateBrowsing'] == True:
                self.establishPBMode(True)
        try: settingsManager.settings['proxy']
        except:
            doNothing()
        else:
            pr = settingsManager.settings['proxy']
            up = ""
            if pr['user'] != "" and pr['password'] != "":
                up = ", qstring(\"" + pr['user'] + "\"), qstring(\"" + pr['password'] + "\")"
            try: pr['type']
            except:
                doNothing()
            else:
                t = pr['type']
                if t == "None":
                    t = "No"
                try: exec("self.page().networkAccessManager().setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy." + t + "Proxy, qstring(\"" + pr['hostname'] + "\"), int(\"" + str(pr['port']) + "\")" + up + "))")
                except:
                    try: exec("self.page().networkAccessManager().setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy." + pr['type'] + "Proxy")
                    except:
                        doNothing()
        aboutDialog.updateUserAgent()
        for child in range(1, len(self.newWindows)):
            try: self.newWindows[child].updateSettings()
            except:
                print("Error! %s does not have an updateSettings() method!" % (self.newWindows[child]))

    def downloadUnsupportedContent(self, reply):
        url = unicode(reply.url().toString())
        try: settingsManager.settings['googleDocsViewerEnabled']
        except:
            d = True
        else:
            d = settingsManager.settings['googleDocsViewerEnabled']
        if d == True and not "file://" in url:
            for ext in app_google_docs_extensions:
                if url.split("?")[0].lower().endswith(ext):
                    self.stop()
                    self.load(QtCore.QUrl("https://docs.google.com/viewer?embedded=true&url=" + url))
                    return
        self.downloadFile(reply.request())

    def printPage(self):
        self.printer = QtGui.QPrinter()
        self.page().mainFrame().render(self.printer.paintEngine().painter())
        q = QtGui.QPrintDialog(self.printer)
        q.open()
        q.accepted.connect(self.finishPrintPage)
        q.exec_()

    def printPreview(self):
        self.printer = QtGui.QPrinter()
        q = QtGui.QPrintPreviewDialog(self.printer, self)
        q.paintRequested.connect(self.print)
        q.exec_()
        q.deleteLater()

    def finishPrintPage(self):
        self.print(self.printer)
        self.printer = None

    def savePage(self):
        self.downloadFile(QtNetwork.QNetworkRequest(self.url()))

    def viewSource(self):
        try: self.sourceViews
        except: self.sourceViews = []
        nm = self.page().networkAccessManager()
        reply = nm.get(QtNetwork.QNetworkRequest(self.url()))
        s = ViewSourceDialog(reply, None)
        self.sourceViews.append(s)
        s.closed.connect(self.removeSourceView)
        s.show()
        s.resize(640, 480)
        s.setWindowIcon(self.icon())

    def removeSourceView(self, o):
        del self.sourceViews[self.sourceViews.index(o)]

    def downloadFile(self, request, fname = ""):
        if not os.path.isdir(os.path.dirname(fname)):
            fname = saveDialog(os.path.split(unicode(request.url().toString()))[1])
        if fname:
            if settingsManager.settings['backend'] == "qt":
                nm = self.page().networkAccessManager()
                if type(request) == QtNetwork.QNetworkReply:
                    reply = nm.get(request.request())
                else:
                    reply = nm.get(request)
                downloadManagerGUI.newReply(reply, fname)
                global downloadStartTimer
                downloadStartTimer.start(250)
            else:
                downloaderThread.setUrl(unicode(request.url().toString()))
                downloaderThread.setDestination(fname)
                username = False
                password = False
                if settingsManager.settings['loginToDownload'] == True:
                    username = inputDialog("Enter a username", "Enter a username here [optional]:")
                    if username.replace(" ", "") != "":
                        password = inputDialog("Enter a username", "Enter a password here [optional]:")
                    else:
                        username = False
                downloaderThread.username = username
                downloaderThread.password = password
                downloaderThread.start()

    def updateTitle(self):
        if self.title() != self.windowTitle():
            t = self.title()
            if self.pb:
                self.setWindowTitle(qstring("%s (PB)" % (unicode(t))))
            else:
                self.setWindowTitle(t)

    def buildNewTabPage(self, forceLoad = True):
        if forceLoad == True:
            self.load(QtCore.QUrl("about:blank"))
        f = str(searchManager.currentSearch.replace("%s", ""))
        if type(self.parent) == Browser:
            t = tr('newTab')
        else:
            t = tr('newWindow')
        html = "<!DOCTYPE html><html><head><title>" + t + "</title><style type='text/css'>h1{margin-top: 0; margin-bottom: 0;}</style></head><body style='font-family: sans-serif;'><b style='display: inline-block;'>" + tr('search') + ":</b><form method='get' action='" + f + "' style='display: inline-block;'><input type='text'  name='q' size='31' maxlength='255' value='' /><input type='submit' value='" + tr('go') + "' /></form><table style='border: 0; margin: 0; padding: 0; width: 100%;' cellpadding='0' cellspacing='0'><tr valign='top'>"
        h = tr('newTabShortcuts')
        try: self.parent.parent.closedTabList
        except:
            doNothing()
        else:
            if len(self.parent.parent.closedTabList) > 0:
                html = html + "<td style='border-right: 1px solid; padding-right: 4px;'><b>" + tr('rCTabs') + "</b><br/>"
            urls = []
            if 1:
                for link in self.parent.parent.closedTabList:
                    breakyes = False
                    for item in urls:
                        if item == link['url']:
                            breakyes = True
                            break
                    if breakyes == True:
                        doNothing()
                    else:
                        html = html + "<a href=\"" + link['url'] + "\">" + link['title'] + "</a><br/>"
                        urls.append(link['url'])
                if len(self.parent.parent.closedTabList) > 0:
                    html = "%s</td>" % (html)
                if not len(self.parent.parent.closedTabList) > 0:
                    h = h.replace("style='padding-left: 4px;'", "")
        html = html + h + "</tr></body></html>"
        self.setHtml(html)

    def locationEdit(self):
        url = inputDialog(tr('openLocation'), tr('enterURL'), self.url().toString())
        if url:
            header = ""
            if not unicode(url).startswith("about:") and not "://" in unicode(url) and not "javascript:" in unicode(url):
                header = "http://"
            url = qstring(header + unicode(url))
            self.load(QtCore.QUrl(url))

    def find(self):
        find = inputDialog(tr('find'), tr('searchFor'), self.text)
        if find:
            self.text = find
        else:
            self.text = ""
        self.findText(self.text, QtWebKit.QWebPage.FindWrapsAroundDocument)

    def findNext(self):
        if not self.text:
            self.find()
        else:
            self.findText(self.text, QtWebKit.QWebPage.FindWrapsAroundDocument)

    def zoom(self, value=1.0):
        self.zoomFactor = value
        self.setZoomFactor(self.zoomFactor)

    def zoomIn(self):
        if self.zoomFactor < 3.0:
            self.zoomFactor = self.zoomFactor + 0.25
            self.setZoomFactor(self.zoomFactor)

    def zoomOut(self):
        if self.zoomFactor > 0.25:
            self.zoomFactor = self.zoomFactor - 0.25
            self.setZoomFactor(self.zoomFactor)

    def zoomReset(self):
        self.zoomFactor = 1.0
        self.setZoomFactor(self.zoomFactor)

    def newWindow(self):
       self.createWindow(QtWebKit.QWebPage.WebBrowserWindow)

    def applyShortcuts(self):
        self.closeWindowAction.setShortcut('Ctrl+W')
        self.newWindowAction.setShortcut('Ctrl+N')
        self.printPageAction.setShortcut('Ctrl+P')
        self.stopAction.setShortcut('Esc')
        self.savePageAction.setShortcut('Ctrl+S')
        self.locationEditAction.setShortcuts(['Ctrl+L', 'Alt+D'])
        self.zoomInAction.setShortcuts(['Ctrl+Shift+=', 'Ctrl+='])
        self.zoomOutAction.setShortcut('Ctrl+-')
        self.zoomResetAction.setShortcut('Ctrl+0')
        self.undoCloseWindowAction.setShortcut("Ctrl+Shift+N")

    def createWindow(self, windowType):
        s = str(len(self.newWindows))
        if settingsManager.settings['oldSchoolWindows'] or settingsManager.settings['openInTabs']:
            if settingsManager.settings['openInTabs']:
                if win.closed:
                    exec("win.show()")
                    exec("win.closed = False")
                    exec("win.resize(800, 480)")
                if self.pb == False:
                    exec("win.newTab()")
                else:
                    exec("win.newpbTab()")
                self.createNewWindow.emit(windowType)
                return win.tabs.widget(win.tabs.currentIndex()).webView
            else:
                if self.pb == True:
                    exec("self.newWindow%s = RWebView(self, True)" % (s))
                else:
                    exec("self.newWindow%s = RWebView(self, False)" % (s))
                exec("self.newWindow%s.buildNewTabPage()" % (s))
                exec("self.newWindow%s.applyShortcuts()" % (s))
                exec("self.newWindow%s.enableControls()" % (s))
                exec("self.newWindow%s.loadControls()" % (s))
                exec("self.newWindow%s.show()" % (s))
                exec("self.newWindows.append(self.newWindow%s)" % (s))
                exec("n = self.newWindow%s" % (s))
                self.createNewWindow.emit(windowType)
                return n
        else:
            if win.closed:
                global win
                if not self.parent == None:
                    exec("win = TabBrowser(self)")
                else:
                    exec("win = TabBrowser()")
                exec("n = win")
            else:
                if not self.parent == None:
                    exec("self.newWindow%s = TabBrowser(self)" % (s))
                else:
                    exec("self.newWindow%s = TabBrowser()" % (s))
                exec("n = self.newWindow%s" % (s))
            n.show()
            return n.tabs.widget(n.tabs.currentIndex()).webView

def undoCloseWindow():
    try:
        global app_windows
        global app_closed_windows
        app_windows.append(app_closed_windows[len(app_closed_windows) - 1])
        del app_closed_windows[len(app_closed_windows) - 1]
    except:
        print("No more windows left!")
    else:
        if type(app_windows[len(app_windows) - 1]) == TabBrowser:
            if app_windows[len(app_windows) - 1].tabs.count() < 1:
                app_windows[len(app_windows) - 1].newTab()
                app_windows[len(app_windows) - 1].tabs.widget(app_windows[len(app_windows) - 1].tabs.currentIndex()).webView.buildNewTabPage()
        app_windows[len(app_windows) - 1].show()

class Browser(QtGui.QMainWindow):
    def __init__(self, parent=None, url=False, pb=False):
        super(Browser, self).__init__()
        self.parent = parent
        self.pb = pb
        self.tempHistory = []
        self.findText = ""
        self.initUI(url)
    def initUI(self, url):
        self.mainToolBar = QtGui.QToolBar("")
        self.mainToolBar.setMovable(False)
        self.mainToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.addToolBar(self.mainToolBar)
        self.centralWidget = QtGui.QWidget()
        self.mainLayout = QtGui.QGridLayout()
        self.centralWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.centralWidget)
        self.mainToolBar.setMovable(False)
        self.mainToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        if app_gnome_unity_integration:
            self.mainToolBar.setStyleSheet("""
            QToolBar {
            border: 0;
            border-bottom: 1px solid palette(shadow);
            background: palette(window);
            }
            """)
        else:
            self.mainToolBar.setStyleSheet("""
            QToolBar {
            border: 0;
            border-bottom: 1px solid palette(shadow);
            background: transparent;
            }
            """)
        self.webView = RWebView(self, self.pb)
        self.updateSettings()

        self.webInspector = QtWebKit.QWebInspector(self)
        self.webInspector.setPage(self.webView.page())
        self.webInspectorDock = QtGui.QDockWidget(tr('webInspector'))
        if app_use_ambiance:
            self.webInspectorDock.setStyleSheet(dw_stylesheet)
        self.webInspectorDock.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        self.webInspectorDock.setWidget(self.webInspector)
        self.addDockWidget(QtCore.Qt.BottomDockWidgetArea, self.webInspectorDock)
        self.webInspectorDock.hide()

        self.historyCompletionBox = QtGui.QWidget()

        self.downArrowAction = QtGui.QAction(self)
        self.downArrowAction.setShortcut("Down")
        self.downArrowAction.triggered.connect(self.historyDown)

        self.historyCompletionBox.addAction(self.downArrowAction)

        self.upArrowAction = QtGui.QAction(self)
        self.upArrowAction.setShortcut("Up")
        self.upArrowAction.triggered.connect(self.historyUp)

        self.historyCompletionBox.addAction(self.upArrowAction)

        self.historyCompletionBoxLayout = QtGui.QVBoxLayout()
        self.historyCompletionBoxLayout.setContentsMargins(0,0,0,0)
        self.historyCompletionBoxLayout.setSpacing(0)
        self.historyCompletionBox.setLayout(self.historyCompletionBoxLayout)
        self.historyCompletionBox.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Popup)
        self.historyCompletion = HistoryCompletionList(self)
        self.historyCompletion.setWordWrap(True)
        self.historyCompletion.itemActivated.connect(self.openHistoryItem)

        self.mainLayout.setSpacing(0);
        self.mainLayout.setContentsMargins(0, 0, 0, 0)

        self.backAction = QtGui.QAction(self)
        self.backAction.setText(tr("back"))
        self.backAction.setToolTip(tr("backBtnTT"))
        self.backAction.triggered.connect(self.webView.back)
        self.backAction.setIcon(QtGui.QIcon().fromTheme("go-previous", QtGui.QIcon(os.path.join(app_icons, 'back.png'))))
        self.mainToolBar.addAction(self.backAction)
        self.mainToolBar.widgetForAction(self.backAction).setFocusPolicy(QtCore.Qt.TabFocus)

        self.nextAction = QtGui.QAction(self)
        self.nextAction.setToolTip(tr("nextBtnTT"))
        self.nextAction.triggered.connect(self.webView.forward)
        self.nextAction.setText("")
        self.nextAction.setIcon(QtGui.QIcon().fromTheme("go-next", QtGui.QIcon(os.path.join(app_icons, 'next.png'))))
        self.mainToolBar.addAction(self.nextAction)
        self.mainToolBar.widgetForAction(self.nextAction).setFocusPolicy(QtCore.Qt.TabFocus)

        historySearchAction = QtGui.QAction(self)
        historySearchAction.triggered.connect(self.parent.focusHistorySearch)
        historySearchAction.setShortcuts(["Alt+H"])
        self.addAction(historySearchAction)

        self.reloadAction = QtGui.QAction(self)
        self.reloadAction.triggered.connect(self.webView.reload)
        self.reloadAction.setText("")
        self.reloadAction.setToolTip(tr("reloadBtnTT"))
        self.reloadAction.setIcon(QtGui.QIcon().fromTheme("view-refresh", QtGui.QIcon(os.path.join(app_icons, 'reload.png'))))
        self.mainToolBar.addAction(self.reloadAction)
        self.mainToolBar.widgetForAction(self.reloadAction).setFocusPolicy(QtCore.Qt.TabFocus)

        self.stopAction = QtGui.QAction(self)
        self.stopAction.setShortcut("Esc")
        self.stopAction.triggered.connect(self.webView.stop)
        self.stopAction.triggered.connect(self.historyCompletionBox.hide)
        self.stopAction.triggered.connect(self.updateText)
        self.stopAction.setText("")
        self.stopAction.setToolTip(tr("stopBtnTT"))
        self.stopAction.setIcon(QtGui.QIcon().fromTheme("process-stop", QtGui.QIcon(os.path.join(app_icons, 'stop.png'))))
        self.mainToolBar.addAction(self.stopAction)
        self.addAction(self.stopAction)
        self.mainToolBar.widgetForAction(self.stopAction).setFocusPolicy(QtCore.Qt.TabFocus)

        self.findAction = QtGui.QAction(self)
        self.findAction.triggered.connect(self.webView.find)
        self.findAction.setText("")
        self.findAction.setToolTip(tr("findBtnTT"))
        self.findAction.setIcon(QtGui.QIcon().fromTheme("edit-find", QtGui.QIcon(os.path.join(app_icons, 'find.png'))))
        self.mainToolBar.addAction(self.findAction)
        self.mainToolBar.widgetForAction(self.findAction).setFocusPolicy(QtCore.Qt.TabFocus)

        self.findNextAction = QtGui.QAction(self)
        self.findNextAction.triggered.connect(self.webView.findNext)
        self.findNextAction.setText("")
        self.findNextAction.setToolTip(tr("findNextBtnTT"))
        self.findNextAction.setIcon(QtGui.QIcon().fromTheme("media-seek-forward", QtGui.QIcon(os.path.join(app_icons, 'find-next.png'))))
        self.mainToolBar.addAction(self.findNextAction)
        self.mainToolBar.widgetForAction(self.findNextAction).setFocusPolicy(QtCore.Qt.TabFocus)

        self.translateAction = QtGui.QAction(self)
        self.translateAction.triggered.connect(self.webView.translate)
        self.translateAction.setShortcut("Alt+Shift+T")
        self.translateAction.setIcon(QtGui.QIcon().fromTheme("preferences-desktop-locale", QtGui.QIcon(os.path.join(app_icons, 'translate.png'))))
        self.translateAction.setToolTip(tr("translateBtnTT"))
        self.mainToolBar.addAction(self.translateAction)
        self.addAction(self.translateAction)
        self.mainToolBar.widgetForAction(self.translateAction).setFocusPolicy(QtCore.Qt.TabFocus)

        self.urlBar = QtGui.QLineEdit()
        self.mainToolBar.addWidget(self.urlBar)

        self.urlBar2 = QtGui.QLineEdit()
        self.historyCompletionBoxLayout.addWidget(self.urlBar2)
        self.historyCompletionBoxLayout.addWidget(self.historyCompletion)

        self.urlBar.setToolTip(tr("locationBarTT"))
        self.urlBar.textChanged.connect(self.rSyncText)
        self.urlBar.textChanged.connect(self.showHistoryBox)

        self.urlBar2.textChanged.connect(self.syncText)
        self.urlBar2.returnPressed.connect(self.updateWeb)
        self.urlBar.returnPressed.connect(self.updateWeb)
        if not self.pb:
            self.urlBar2.textChanged.connect(self.searchHistory)
        self.webView.urlChanged.connect(self.updateText)
        self.webView.urlChanged.connect(self.enableDisableBF)
        if not self.pb:
            self.webView.urlChanged.connect(browserHistory.reload)
            self.webView.titleChanged.connect(browserHistory.reload)
            self.webView.urlChanged.connect(browserHistory.append)
            self.webView.titleChanged.connect(browserHistory.updateTitles)
        searchAction = QtGui.QAction(self)
        searchAction.setShortcut("Ctrl+K")
        searchAction.triggered.connect(self.searchWeb)
        self.addAction(searchAction)
        self.historyCompletionBox.addAction(searchAction)


        self.addBookmarkButton = QtGui.QToolButton(self)
        self.addBookmarkButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.addBookmarkButton.clicked.connect(self.bookmarkPage)
        self.addBookmarkButton.setText("")
        self.addBookmarkButton.setToolTip(tr("addBookmarkTT"))
        self.addBookmarkButton.setShortcut("Ctrl+D")
        self.addBookmarkButton.setIcon(QtGui.QIcon().fromTheme("emblem-favorite", QtGui.QIcon(os.path.join(app_icons, 'heart.png'))))
        self.addBookmarkButton.setIconSize(QtCore.QSize(16, 16))
        self.mainToolBar.addWidget(self.addBookmarkButton)

        self.goButton = QtGui.QToolButton(self)
        self.goButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.goButton.clicked.connect(self.updateWeb)
        self.goButton.setText("")
        self.goButton.setToolTip(tr("go"))
        self.goButton.setIcon(QtGui.QIcon().fromTheme("go-jump", QtGui.QIcon(os.path.join(app_icons, 'go.png'))))
        self.goButton.setIconSize(QtCore.QSize(16, 16))
        self.mainToolBar.addWidget(self.goButton)

        self.searchButton = QtGui.QPushButton(self)
        self.searchButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.searchButton.clicked.connect(self.searchWeb)
        self.searchButton.setText(tr("searchBtn"))
        self.searchButton.setToolTip(tr("searchBtnTT"))
        self.mainToolBar.addWidget(self.searchButton)

        self.searchEditButtonContainer = QtGui.QWidget(self)
        self.searchEditButtonContainerLayout = QtGui.QVBoxLayout(self)
        self.searchEditButtonContainerLayout.setSpacing(0);
        self.searchEditButtonContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.searchEditButtonContainer.setLayout(self.searchEditButtonContainerLayout)
        self.searchEditButton = QtGui.QToolButton(self)
        self.searchEditButton.setStyleSheet("QToolButton { max-width: 20px; }")
        self.searchEditButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.searchEditButton.setToolTip(tr("searchBtnTT"))
        self.searchEditButton.clicked.connect(self.editSearch)
        self.searchEditButton.setShortcut("Ctrl+Shift+K")
        self.searchEditButton.setToolTip(tr("editSearchTT"))
        self.searchEditButton.setArrowType(QtCore.Qt.DownArrow)
        self.searchEditButtonContainerLayout.addWidget(self.searchEditButton)
        self.mainToolBar.addWidget(self.searchEditButtonContainer)

        self.focusURLBarAction = QtGui.QAction(self)
        self.historyCompletionBox.addAction(self.focusURLBarAction)
        self.focusURLBarAction.setShortcuts(["Alt+D", "Ctrl+L"])
        self.focusURLBarAction.triggered.connect(self.focusURLBar)
        self.addAction(self.focusURLBarAction)
        self.mainLayout.addWidget(self.webView, 2, 0)
        self.webView.settings().setIconDatabasePath(qstring(app_profile))
        self.webView.page().linkHovered.connect(self.updateStatusMessage)

        # Status bar
        self.statusBarBorder = QtGui.QWidget()
        self.statusBarBorder.setStyleSheet("""
        background: palette(shadow);
        """)
        self.statusBarBorder.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed))
        self.statusBarBorder.setMinimumHeight(1)
        self.mainLayout.addWidget(self.statusBarBorder, 3, 0)
        self.statusBar = QtGui.QFrame()
        self.statusBar.setStyleSheet("""
        QFrame {
        background: palette(window);
        border: 0;
        }
        """)
        self.mainLayout.addWidget(self.statusBar, 4, 0)
        self.statusBarLayout = QtGui.QHBoxLayout()
        self.statusBarLayout.setContentsMargins(0,0,0,0)        
        self.statusBar.setLayout(self.statusBarLayout)
        self.statusMessage = QtGui.QLineEdit()
        self.statusMessage.setReadOnly(True)
        self.statusMessage.setFocusPolicy(QtCore.Qt.TabFocus)
        self.historyCompletion.statusMessage.connect(self.statusMessage.setText)
        self.statusMessage.setStyleSheet("""
        QLineEdit {
        min-height: 1em;
        max-height: 1em;
        border: 0;
        background: transparent;
        }
        """)
        self.statusBarLayout.addWidget(self.statusMessage)
        self.progressBar = QtGui.QProgressBar()
        self.progressBar.hide()
        self.webView.loadFinished.connect(self.progressBar.hide)
        self.webView.loadProgress.connect(self.progressBar.setValue)
        self.webView.loadProgress.connect(self.progressBar.show)
        self.progressBar.setStyleSheet("""
        min-height: 1em;
        max-height: 1em;
        min-width: 200px;
        max-width: 200px;
        """)
        self.statusBarLayout.addWidget(self.progressBar)
        self.zoomBar = QtGui.QWidget()
        self.zoomBar.setStyleSheet("""
        QToolButton, QPushButton {
        min-width: 16px;
        min-height: 1em;
        max-height: 1em;
        padding-left: 4px;
        padding-right: 4px;
        border-radius: 4px;
        border: 1px solid palette(shadow);
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(light), stop:1 palette(button));
        }

        QToolButton:pressed, QPushButton:pressed {
        border: 1px solid palette(shadow);
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(shadow), stop:1 palette(button));
        }
        """)
        self.statusBarLayout.addWidget(self.zoomBar)
        self.zoomBarLayout = QtGui.QHBoxLayout()
        self.zoomBarLayout.setContentsMargins(0,2,0,0)
        self.zoomBarLayout.setSpacing(0)
        self.zoomBar.setLayout(self.zoomBarLayout)
        
        self.zoomOutButton = QtGui.QPushButton("-")
        self.zoomOutButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.zoomSlider = QtGui.QSlider()
        self.zoomSlider.setStyleSheet("max-height: 1em;")
        self.zoomSlider.setFocusPolicy(QtCore.Qt.TabFocus)
        self.zoomSlider.setSizePolicy(QtGui.QSizePolicy(QtGui.QSizePolicy.Preferred, QtGui.QSizePolicy.Fixed))
        self.zoomSlider.setOrientation(QtCore.Qt.Horizontal)
        self.zoomSlider.setMinimum(1)
        self.zoomSlider.setMaximum(12)
        self.zoomSlider.setSliderPosition(4)
        self.zoomSlider.setTickInterval(1)
        self.zoomSlider.setTickPosition(QtGui.QSlider.TicksBelow)
        self.zoomSlider.setMinimumWidth(128)
        self.zoomInButton = QtGui.QPushButton("+")
        self.zoomInButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.zoomLabel = QtGui.QLabel("1.00x")
        self.zoomLabel.setStyleSheet("margin-left: 2px;")
        self.zoomBarLayout.addWidget(self.zoomOutButton)
        self.zoomBarLayout.addWidget(self.zoomSlider)
        self.zoomBarLayout.addWidget(self.zoomInButton)
        self.zoomBarLayout.addWidget(self.zoomLabel)

        self.webView.statusBarMessage.connect(self.statusMessage.setText)

        if not url == False and not url == "":
            self.urlBar.setText(qstring(url))
            self.updateWeb()
        self.updateText()
        self.zoomOutAction = QtGui.QAction(self)
        self.zoomOutAction.setShortcut("Ctrl+-")
        self.zoomOutAction.triggered.connect(self.zoomOut)
        self.addAction(self.zoomOutAction)
        self.zoomInAction = QtGui.QAction(self)
        self.zoomInAction.setShortcuts(["Ctrl+Shift+=", "Ctrl+="])
        self.zoomInAction.triggered.connect(self.zoomIn)
        self.addAction(self.zoomInAction)
        self.zoomResetAction = QtGui.QAction(self)
        self.zoomResetAction.setShortcut("Ctrl+0")
        self.zoomResetAction.triggered.connect(self.zoomReset)
        self.addAction(self.zoomResetAction)
        self.zoomOutButton.clicked.connect(self.zoomOut)
        self.zoomInButton.clicked.connect(self.zoomIn)
        self.zoomSlider.valueChanged.connect(self.zoom)
        self.webView.show()
        self.enableDisableBF()

    def enableDisableBF(self):
        if self.webView.page().history().canGoBack():
            self.mainToolBar.widgetForAction(self.backAction).setEnabled(True)
        else:
            self.mainToolBar.widgetForAction(self.backAction).setEnabled(False)
        if self.webView.page().history().canGoForward():
            self.mainToolBar.widgetForAction(self.nextAction).setEnabled(True)
        else:
            self.mainToolBar.widgetForAction(self.nextAction).setEnabled(False)

    def historyUp(self):
        if self.historyCompletion.currentRow() == 0 and self.historyCompletion.hasFocus():
            self.historyCompletion.setFocus(False)
            self.urlBar2.setFocus(True)
        elif not self.urlBar2.hasFocus():
            self.historyCompletion.setCurrentRow(self.historyCompletion.currentRow() - 1)
        else:
            self.urlBar2.setFocus(False)
            self.historyCompletion.setFocus(True)
            self.historyCompletion.setCurrentRow(self.historyCompletion.count() - 1)

    def historyDown(self):
        if self.urlBar2.hasFocus():
            self.historyCompletion.setCurrentRow(0)
            self.urlBar2.setFocus(False)
            self.historyCompletion.setFocus(True)
        elif not self.historyCompletion.currentRow() == self.historyCompletion.count() - 1:
            self.historyCompletion.setCurrentRow(self.historyCompletion.currentRow() + 1)
        else:
            self.historyCompletion.setFocus(False)
            self.urlBar2.setFocus(True)

    def zoomIn(self):
        self.zoomSlider.setValue(self.zoomSlider.value() + 1)

    def zoomOut(self):
        self.zoomSlider.setValue(self.zoomSlider.value() - 1)

    def zoomReset(self):
        self.zoomSlider.setValue(4)
        
    def zoom(self, value):
        self.webView.setZoomFactor(float(value) * 0.25)
        self.zoomLabel.setText(qstring("%.2fx" % (float(value) * 0.25)))

    def updateStatusMessage(self, link="", title="", content=""):
        self.statusMessage.setText(qstring(link))

    def updateSettings(self):
        self.webView.updateSettings()

    def showHistoryBox(self):
        if not self.historyCompletionBox.isVisible():
            if not self.urlBar.text() == self.webView.url().toString():
                self.urlBar2.setFocus(True)
                self.historyCompletionBox.move(self.urlBar.mapToGlobal(QtCore.QPoint(0,0)).x(), self.urlBar.mapToGlobal(QtCore.QPoint(0,0)).y())
                self.historyCompletionBox.show()
                self.historyCompletionBox.resize(self.urlBar.width(), self.historyCompletionBox.height())

    def searchHistory(self, string):
        string = unicode(string)
        if string != "" and string != unicode(self.webView.url().toString()) and string != "about:version":
            self.searchOn = True
            self.historyCompletion.clear()
            history = []
            string = unicode(string)
            for item in browserHistory.history:
                add = False
                for subitem in item:
                    if string.lower() in unicode(item[subitem]).lower():
                        add = True
                        break
                if add == True:
                    history.append(item)
                    self.historyCompletion.addItem(item['name'])
            self.tempHistory = history
        else:
            self.historyCompletionBox.hide()
    def openHistoryItem(self, item):
        self.webView.load(QtCore.QUrl(self.tempHistory[self.historyCompletion.row(item)]['url']))
        self.historyCompletionBox.hide()
        self.webView.show()
    def licensing(self):
        url = QtCore.QUrl(os.path.join(app_lib, "LICENSE.html"))
        self.webView.load(url)

    def searchWeb(self):
        urlBar = self.urlBar.text()
        url = QtCore.QUrl(searchManager.currentSearch.replace("%s", urlBar))
        self.webView.load(url)

    def editSearch(self):
        searchEditor.display(True, self.searchEditButton.mapToGlobal(QtCore.QPoint(0,0)).x(), self.searchEditButton.mapToGlobal(QtCore.QPoint(0,0)).y(), self.searchEditButton.width(), self.searchEditButton.height())

    def focusURLBar(self):
        if not self.historyCompletionBox.isVisible():
            self.urlBar.setFocus()
            self.urlBar.selectAll()
        else:
            self.urlBar2.setFocus()
            self.urlBar2.selectAll()

    def bookmarkPage(self):
        name = inputDialog(tr('addBookmark'), tr('enterName'), unicode(self.webView.title()))
        if name and name != "":
            bookmarksManager.add(unicode(self.webView.url().toString()), unicode(name))

    def updateWeb(self):
        urlBar = self.urlBar.text()
        urlBar = unicode(urlBar)
        header = ""
        search = False
        for key in searchManager.searchEngines:
            if urlBar.startswith("%s " % (searchManager.searchEngines[key]['keyword'])):
                search = searchManager.searchEngines[key]
                break
        if search:
            urlBar = urlBar.replace("%s " % (search['keyword']), "")
            urlBar = QtCore.QUrl(search['expression'].replace("%s", urlBar))
            self.webView.load(urlBar)
        else:
            if not unicode(urlBar).startswith("about:") and not "://" in unicode(urlBar) and " " in unicode(urlBar):
                self.searchWeb()
            else:
                if os.path.exists(unicode(urlBar)):
                    header = "file://"
                elif not unicode(urlBar).startswith("about:") and not "://" in unicode(urlBar) and not "javascript:" in unicode(urlBar):
                    header = "http://"
                if unicode(urlBar) == "about:" or unicode(urlBar) == "about:version":
                    showAboutPage(self.webView)
                else:
                    url = qstring(header + unicode(urlBar))
                    url = QtCore.QUrl(url)
                    self.webView.load(url)
    def syncText(self):
        self.urlBar.setText(self.urlBar2.text())
    def rSyncText(self):
        if self.urlBar2.text() != self.urlBar.text():
            self.urlBar2.setText(self.urlBar.text())
    def updateText(self):
        url = self.webView.url()
        texturl = url.toString()
        self.urlBar2.setText(texturl)

downloaderThread = DownloaderThread()

class CDialog(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(CDialog, self).__init__()
        self.parent = parent
        self.settings = {}
        self.initUI()
        self.filterListCount = 0
        self.resize(400, 400)
    def initUI(self):
        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Ctrl+Alt+P", "Esc"])
        closeWindowAction.triggered.connect(self.close)
        self.addAction(closeWindowAction)

        self.setWindowTitle(tr('preferences'))
        self.setWindowIcon(QtGui.QIcon(app_logo))
        self.tabs = QtGui.QTabWidget()
        self.setCentralWidget(self.tabs)

        # General settings page
        self.generalWidget = QtGui.QWidget()
        self.gLayout = QtGui.QVBoxLayout()
        self.generalWidget.setLayout(self.gLayout)
        self.tabs.addTab(self.generalWidget, tr('general'))

        # Content settings page
        self.cWidget = QtGui.QWidget()
        self.cLayout = QtGui.QVBoxLayout()
        self.cWidget.setLayout(self.cLayout)
        self.tabs.addTab(self.cWidget, tr('content'))

        # Data settings page
        self.aWidget = QtGui.QWidget()
        self.aLayout = QtGui.QVBoxLayout()
        self.aWidget.setLayout(self.aLayout)
        self.tabs.addTab(self.aWidget, tr('data'))

        # Browsing settings page
        self.pWidget = QtGui.QWidget()
        self.pLayout = QtGui.QVBoxLayout()
        self.pWidget.setLayout(self.pLayout)
        self.tabs.addTab(self.pWidget, tr('browsing'))

        # Download settings page
        self.dWidget = QtGui.QWidget()
        self.dLayout = QtGui.QVBoxLayout()
        self.dWidget.setLayout(self.dLayout)
        self.tabs.addTab(self.dWidget, tr('downloadsHKey'))

        newWindowBox = QtGui.QLabel(tr('newWindowOption0'))
        self.gLayout.addWidget(newWindowBox)
        self.openTabsBox = QtGui.QCheckBox(tr('newWindowOption'))
        self.openTabsBox.stateChanged.connect(self.checkOSWBox)
        self.gLayout.addWidget(self.openTabsBox)
        self.oswBox = QtGui.QCheckBox(tr('newWindowOption2'))
        self.oswBox.stateChanged.connect(self.checkOTabsBox)
        self.gLayout.addWidget(self.oswBox)
        uCloseLabel = QtGui.QLabel(tr('maxUndoCloseTab') + ":")
        self.gLayout.addWidget(uCloseLabel)
        self.undoCloseTabCount = QtGui.QLineEdit()
        self.undoCloseTabCount.setInputMask(qstring("#90"))
        self.gLayout.addWidget(self.undoCloseTabCount)
        uCloseNoteLabel = QtGui.QLabel(tr('maxUndoCloseTabNote'))
        self.gLayout.addWidget(uCloseNoteLabel)
        self.imagesBox = QtGui.QCheckBox(tr('autoLoadImages'))
        self.cLayout.addWidget(self.imagesBox)
        self.jsBox = QtGui.QCheckBox(tr('enableJS'))
        self.cLayout.addWidget(self.jsBox)
        self.storageBox = QtGui.QCheckBox(tr('enableStorage'))
        self.cLayout.addWidget(self.storageBox)
        self.pluginsBox = QtGui.QCheckBox(tr('enablePlugins'))
        self.cLayout.addWidget(self.pluginsBox)

        self.gDocsBox = QtGui.QCheckBox(tr('enableGDViewer'))
        self.cLayout.addWidget(self.gDocsBox)

        self.pbBox = QtGui.QCheckBox(tr('enablePB'))
        self.pLayout.addWidget(self.pbBox)

        self.aBBox = QtGui.QCheckBox(tr('enableAB'))
        self.aBBox.stateChanged.connect(self.tryDownload)
        downloaderThread.fileDownloaded.connect(self.applyFilters)
        self.cLayout.addWidget(self.aBBox)
        self.uALabel1 = QtGui.QLabel(tr("userAgent") + ":")
        self.cLayout.addWidget(self.uALabel1)
        self.uABox = QtGui.QLineEdit()
        self.cLayout.addWidget(self.uABox)
        self.uALabel2 = QtGui.QLabel(tr("customUserAgent"))
        self.cLayout.addWidget(self.uALabel2)
        self.cLayout.addWidget(RExpander())
        backendBox = QtGui.QLabel(tr('downloadBackend'))
        backendBox.setSizePolicy(QtGui.QSizePolicy.Fixed, QtGui.QSizePolicy.Fixed)
        self.dLayout.addWidget(backendBox)
        self.selectBackend = QtGui.QComboBox()
        self.selectBackend.addItem('qt')
        self.selectBackend.addItem('python')
        self.selectBackend.addItem('aria2')
        self.selectBackend.addItem('axel')
        self.dLayout.addWidget(self.selectBackend)
        self.lDBox = QtGui.QCheckBox(tr('loginToDownload'))
        self.dLayout.addWidget(self.lDBox)
        self.dLayout.addWidget(RExpander())
        self.editSearchButton = QtGui.QPushButton(tr('manageSearchEngines'))
        try: self.editSearchButton.clicked.connect(searchEditor.display)
        except:
            doNothing()
        self.gLayout.addWidget(self.editSearchButton)
        self.gLayout.addWidget(RExpander())

        # Proxy configuration stuff
        proxyBox = QtGui.QLabel(tr('proxyConfig'))
        self.pLayout.addWidget(proxyBox)
        self.proxySel = QtGui.QComboBox()
        self.proxySel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.proxySel.addItem("None")
        self.proxySel.addItem('Socks5')
        self.proxySel.addItem('Http')
        sLabel = QtGui.QLabel(tr('type') + ":")
        l0 = RHBoxLayout()
        l0.addWidget(sLabel)
        l0.addWidget(self.proxySel)
        l0l = QtGui.QWidget()
        l0l.setLayout(l0)
        self.pLayout.addWidget(l0l)
        hLabel = QtGui.QLabel(tr('hostname') + ":")
        self.hostnameBox = QtGui.QLineEdit()
        l1 = RHBoxLayout()
        l1.addWidget(hLabel)
        l1.addWidget(self.hostnameBox)
        l1l = QtGui.QWidget()
        l1l.setLayout(l1)
        self.pLayout.addWidget(l1l)
        p1Label = QtGui.QLabel(tr('port') + ":")
        self.portBox = QtGui.QLineEdit()
        l2 = RHBoxLayout()
        l2.addWidget(p1Label)
        l2.addWidget(self.portBox)
        l2l = QtGui.QWidget()
        l2l.setLayout(l2)
        self.pLayout.addWidget(l2l)
        uLabel = QtGui.QLabel(tr('user') + ":")
        self.userBox = QtGui.QLineEdit()
        l3 = RHBoxLayout()
        l3.addWidget(uLabel)
        l3.addWidget(self.userBox)
        l3l = QtGui.QWidget()
        l3l.setLayout(l3)
        self.pLayout.addWidget(l3l)
        p2Label = QtGui.QLabel(tr('password') + ":")
        self.passwordBox = QtGui.QLineEdit()
        l4 = RHBoxLayout()
        l4.addWidget(p2Label)
        l4.addWidget(self.passwordBox)
        l4l = QtGui.QWidget()
        l4l.setLayout(l4)
        self.pLayout.addWidget(l4l)

        self.pLayout.addWidget(RExpander())

        # Data Management
        self.clearHistoryButton = QtGui.QPushButton(tr('clearHistory'))
        self.clearHistoryButton.clicked.connect(self.showHistoryDialog)
        self.aLayout.addWidget(self.clearHistoryButton)

        sProfileLabel = QtGui.QLabel(tr('selectProfile') + ":")
        self.profileList = QtGui.QListWidget()
        self.addProfileButton = QtGui.QPushButton(tr("addProfile"))
        self.addProfileButton.clicked.connect(self.addProfile)
        self.aLayout.addWidget(sProfileLabel)
        self.aLayout.addWidget(self.profileList)
        self.aLayout.addWidget(self.addProfileButton)

        cloudLabel = QtGui.QLabel(tr("cloudService"))
        cloudLabel.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        cloudLabel2 = QtGui.QLabel(tr("cloudService2"))
        cloudLabel2.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
        self.cloudBox = QtGui.QComboBox()
        self.cloudBox.addItem("No")
        self.cloudBox.addItem("Dropbox")
        self.cloudBox.addItem("Ubuntu One")
        self.aLayout.addWidget(cloudLabel)
        self.aLayout.addWidget(self.cloudBox)
        self.aLayout.addWidget(cloudLabel2)

        self.aLayout.addWidget(RExpander())

        self.cToolBar = QtGui.QToolBar()
        self.cToolBar.setStyleSheet(blanktoolbarsheet)
        self.cToolBar.setMovable(False)
        self.cToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        applyAction = QtGui.QPushButton(tr('apply'))
        applyAction.setShortcut("Ctrl+S")
        applyAction.clicked.connect(self.saveSettings)
        closeAction = QtGui.QPushButton(tr('close'))
        closeAction.clicked.connect(self.hide)
        self.cToolBar.addWidget(applyAction)
        self.cToolBar.addWidget(closeAction)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.cToolBar)
        self.loadSettings()
        settingsManager.saveSettings()
    def showHistoryDialog(self):
        clearHistoryDialog.display()    

    def checkOSWBox(self):
        if self.openTabsBox.isChecked():
            self.oswBox.setCheckState(QtCore.Qt.Unchecked)
    def checkOTabsBox(self):
        if self.oswBox.isChecked():
            self.openTabsBox.setCheckState(QtCore.Qt.Unchecked)
    def applyFilters(self):
        l = os.listdir(os.path.join(app_profile, "adblock"))
        if len(l) != self.filterListCount:
            settingsManager.applyFilters()
            self.filterListCount = len(l)
    def tryDownload(self):
        if self.aBBox.isChecked():
            l = os.listdir(os.path.join(app_profile, "adblock"))
            if len(l) == 0:
                downloaderThread.setUrl("https://easylist-downloads.adblockplus.org/easylist.txt")
                downloaderThread.setDestination(os.path.join(app_profile, "adblock", "easylist.txt"))
                downloaderThread.start()
    def loadSettings(self):
        if not os.path.exists(app_profile):
            os.makedirs(app_profile)
        settingsManager.loadSettings()
        self.settings = settingsManager.settings
        try: self.settings['openInTabs']
        except:
            self.openTabsBox.setChecked(True)
        else:
            self.openTabsBox.setChecked(self.settings['openInTabs'])
        try: self.settings['oldSchoolWindows']
        except:
            self.oswBox.setChecked(False)
        else:
            self.oswBox.setChecked(self.settings['oldSchoolWindows'])
        try: self.settings['loadImages']
        except: 
            self.imagesBox.setChecked(True)
        else:
            self.imagesBox.setChecked(self.settings['loadImages'])
        try: self.settings['jsEnabled']
        except: 
            self.jsBox.setChecked(True)
        else:
            self.jsBox.setChecked(self.settings['jsEnabled'])
        try: self.settings['storageEnabled']
        except: 
            self.storageBox.setChecked(True)
        else:
            self.storageBox.setChecked(self.settings['storageEnabled'])
        try: self.settings['pluginsEnabled']
        except:
            if sys.platform.startswith("linux"):
                self.pluginsBox.setChecked(False)
            else:
                self.pluginsBox.setChecked(True)
        else:
            self.pluginsBox.setChecked(self.settings['pluginsEnabled'])
        try: self.settings['privateBrowsing']
        except: 
            self.pbBox.setChecked(False)
        else:
            self.pbBox.setChecked(self.settings['privateBrowsing'])
        try: self.settings['loginToDownload']
        except: 
            self.lDBox.setChecked(False)
        else:
            self.lDBox.setChecked(self.settings['loginToDownload'])
        try: self.settings['googleDocsViewerEnabled']
        except: 
            self.gDocsBox.setChecked(True)
        else:
            self.gDocsBox.setChecked(self.settings['googleDocsViewerEnabled'])
        try: self.settings['adBlock']
        except: 
            self.aBBox.setChecked(False)
        else:
            self.aBBox.setChecked(self.settings['adBlock'])
        try: self.settings['customUserAgent']
        except:
            doNothing()
        else:
            self.uABox.setText(self.settings['customUserAgent'])
        try: self.settings['backend']
        except:
            doNothing()
        else:
            downloaderThread.backend = self.settings['backend']
            for index in range(0, self.selectBackend.count()):
                try: self.selectBackend.itemText(index)
                except:
                    doNothing()
                else:
                    if unicode(self.selectBackend.itemText(index)).lower() == self.settings['backend']:
                        self.selectBackend.setCurrentIndex(index)
                        break
            qtb = os.path.join(app_profile, "qtbck.conf")
            if not os.path.exists(qtb):
                self.selectBackend.setCurrentIndex(0)
                f = open(qtb, "w")
                f.write("")
                f.close()
                self.saveSettings()
        try: self.settings['maxUndoCloseTab']
        except:
            self.undoCloseTabCount.setText("-1")
        else:
            self.undoCloseTabCount.setText(str(self.settings['maxUndoCloseTab']))
        try: self.settings['proxy']
        except:
            doNothing()
        else:
            pr = self.settings['proxy']
            if pr['type']:
                for i in range(self.proxySel.count()):
                    u = self.proxySel.itemText(i)
                    if pr['type'] == u:
                        self.proxySel.setCurrentIndex(i)
                        break
            if pr['hostname']:
                self.hostnameBox.setText(pr['hostname'])
            if pr['port']:
                self.portBox.setText(pr['port'])
            if pr['user']:
                self.userBox.setText(pr['user'])
            if pr['password']:
                self.portBox.setText(pr['password'])
        try: self.settings['cloudService']
        except:
            doNothing()
        else:
            for i in range(self.cloudBox.count()):
                u = self.cloudBox.itemText(i)
                if self.settings['cloudService'] == u:
                    self.cloudBox.setCurrentIndex(i)
                    break
        self.reloadProfiles()
        if os.path.exists(app_default_profile_file):
            f = open(app_default_profile_file)
            d = f.read().replace("\n", "")
            f.close()
            for i in range(self.profileList.count()):
                u = self.profileList.item(i).text()
                if unicode(u) == d:
                    self.profileList.setCurrentRow(i)
                    break
        else:
            for i in range(self.profileList.count()):
                u = self.profileList.item(i).text()
                if unicode(u) == app_default_profile_name:
                    self.profileList.setCurrentRow(i)
                    break
        try:
            global app_windows
            for window in app_windows:
                try:
                    window.updateSettings()
                except:
                    doNothing()
        except:
            doNothing()
    def addProfile(self):
        pname = inputDialog(tr('query'), tr('enterProfileName'))
        if pname:
            try: os.makedirs(os.path.join(app_profile_folder, unicode(pname)))
            except:
                message(tr("error"), tr("profileError2"), "warn")
        self.reloadProfiles()
        for i in range(self.profileList.count()):
            u = self.profileList.item(i).text()
            if unicode(u) == app_default_profile_name:
                self.profileList.setCurrentRow(i)
                break
    def reloadProfiles(self):
        self.profileList.clear()
        l = os.listdir(app_profile_folder)
        for profile in l:
            if os.path.isdir(os.path.join(app_profile_folder, profile)):
                self.profileList.addItem(profile)
    def saveSettings(self):
        if unicode(self.undoCloseTabCount.text()) == "":
            self.undoCloseTabCount.setText("-1")
        self.settings = {'openInTabs' : self.openTabsBox.isChecked(), 'oldSchoolWindows' : self.oswBox.isChecked(), 'loadImages' : self.imagesBox.isChecked(), 'jsEnabled' : self.jsBox.isChecked(), 'storageEnabled' : self.storageBox.isChecked(), 'pluginsEnabled' : self.pluginsBox.isChecked(), 'privateBrowsing' : self.pbBox.isChecked(), 'backend' : unicode(self.selectBackend.currentText()).lower(), 'loginToDownload' : self.lDBox.isChecked(), 'adBlock' : self.aBBox.isChecked(), 'proxy' : {"type" : unicode(self.proxySel.currentText()), "hostname" : unicode(self.hostnameBox.text()), "port" : unicode(self.portBox.text()), "user" : unicode(self.userBox.text()), "password" : unicode(self.passwordBox.text())}, "cloudService" : unicode(self.cloudBox.currentText()), 'maxUndoCloseTab' : int(unicode(self.undoCloseTabCount.text())), 'googleDocsViewerEnabled' : self.gDocsBox.isChecked(), 'customUserAgent' : unicode(self.uABox.text())}
        f = open(app_default_profile_file, "w")
        f.write(unicode(self.profileList.currentItem().text()))
        f.close()
        settingsManager.settings = self.settings
        settingsManager.setBackend(unicode(self.selectBackend.currentText()).lower())
        settingsManager.saveSettings()
        global app_windows
        for window in app_windows:
            try:
                window.updateSettings()
            except:
                doNothing()
        local_app_profile = os.path.join(app_profile_folder, app_profile_name)
        if settingsManager.settings['cloudService'] == "No":
            if os.path.exists(os.path.join(local_app_profile, "settings.json")):
                os.remove(os.path.join(local_app_profile, "settings.json"))
            shutil.copy(os.path.join(app_profile, "settings.json"), local_app_profile)

cDialog = None

class TabBrowser(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(TabBrowser, self).__init__()
        self.parent = parent
        if os.path.exists(app_logo):
            if not sys.platform.startswith("win"):
                self.setWindowIcon(QtGui.QIcon(app_logo))
            else:
                if os.path.exists(os.path.join(app_icons, 'about-logo.png')):
                    self.setWindowIcon(QtGui.QIcon(os.path.join(app_icons, 'about-logo.png')))
        self.tabCount = 0
        self.closed = False
        self.closedTabList = []
        self.searchOn = False
        self.tempHistory = []

        self.urlCheckTimer = QtCore.QTimer()
        self.urlCheckTimer.timeout.connect(self.checkForURLs)
        self.urlCheckTimer.start(250)

        global app_windows
        app_windows.append(self)

        self.rebuildLock()

        self.mouseX = False
        self.mouseY = False

        self.initUI()

    def mousePressEvent(self, ev):
        if ev.button() == QtCore.Qt.RightButton:
            self.showTabsContextMenu()
        else:
            self.mouseX = ev.globalX()
            self.origX = self.x()
            self.mouseY = ev.globalY()
            self.origY = self.y()

    def mouseMoveEvent(self, ev):
        if self.mouseX and self.mouseY and not self.isMaximized():
            self.move(self.origX + ev.globalX() - self.mouseX,
self.origY + ev.globalY() - self.mouseY)

    def mouseReleaseEvent(self, ev):
        self.mouseX = False
        self.mouseY = False

    def checkForURLs(self):
        if os.path.exists(app_instance2) and not self.closed:
            f = open(app_instance2)
            i2contents = f.readlines()
            f.close()
            os.remove(app_instance2)
            for item in i2contents:
                item = item.replace("\n", "")
                if not "://" in item and not "about:" in item and not item == "":
                    item = "http://%s" % (item)
                if not item == "":
                    self.newTab(item)
        if self.closed:
            self.urlCheckTimer.stop()

    def rebuildLock(self):
        if not os.path.exists(app_lock):
            f = open(app_lock, "w")
            f.write("")
            f.close()

    def checkTempFiles(self):
        if app_kill_temp_files == True:
            shred_directory(os.path.join(app_profile, "temp"))

    def quit(self):
        q = QtGui.QMessageBox.Yes
        if downloadManagerGUI.progress > 0.0:
            q = QtGui.QMessageBox.question(None, tr("warning"),
        tr("downloadsInProgress"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if q == QtGui.QMessageBox.Yes:
            self.close()
            QtCore.QCoreApplication.instance().quit()

    def closeEvent(self, ev):
        global app_windows
        if self in app_windows:
            del app_windows[app_windows.index(self)]
            global app_closed_windows
            if len(app_closed_windows) >= 10:
                del app_closed_windows[0]
            app_closed_windows.append(self)
        self.closed = True
        return QtGui.QMainWindow.closeEvent(self, ev)

    def aboutRyoukoHKey(self):
        aboutDialog.show()

    def initUI(self):

        # Quit action
        quitAction = QtGui.QAction(tr("quit"), self)
        quitAction.setShortcut("Ctrl+Shift+Q")
        quitAction.triggered.connect(self.quit)
        self.addAction(quitAction)

        # History sidebar
        self.historyDock = QtGui.QDockWidget(tr('history'))
        if app_use_ambiance:
            self.historyDock.setStyleSheet(dw_stylesheet)
        self.historyDock.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        self.historyDockWindow = QtGui.QMainWindow()
        self.historyToolBar = QtGui.QToolBar("History Toolbar")
        self.historyToolBar.setStyleSheet(blanktoolbarsheet)
        self.historyToolBar.setMovable(False)
        self.historyList = QtGui.QListWidget()
        self.historyList.itemActivated.connect(self.openHistoryItem)
        deleteHistoryItemAction = QtGui.QAction(self)
        deleteHistoryItemAction.setShortcut("Del")
        deleteHistoryItemAction.triggered.connect(self.deleteHistoryItem)
        self.addAction(deleteHistoryItemAction)
        self.searchHistoryField = QtGui.QLineEdit()
        self.searchHistoryField.textChanged.connect(self.searchHistory)
        clearHistoryAction = QtGui.QAction(QtGui.QIcon.fromTheme("edit-clear", QtGui.QIcon(os.path.join(app_icons, "clear.png"))), tr('clearHistoryHKey'), self)
        clearHistoryAction.setToolTip(tr('clearHistoryTT'))
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(self.showClearHistoryDialog)
        self.addAction(clearHistoryAction)
        self.historyToolBar.addWidget(self.searchHistoryField)
        self.historyToolBar.addAction(clearHistoryAction)
        self.historyDockWindow.addToolBar(self.historyToolBar)
        self.historyDockWindow.setCentralWidget(self.historyList)
        self.historyDock.setWidget(self.historyDockWindow)
        browserHistory.historyChanged.connect(self.reloadHistory)
        self.reloadHistory()
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.historyDock)
        self.historyDock.hide()

        # Bookmarks manager! FINALLY! Yay!
        manageBookmarksAction = QtGui.QAction(tr('viewBookmarks'), self)
        manageBookmarksAction.setShortcuts(["Ctrl+Shift+O", "Ctrl+Shift+B"])
        manageBookmarksAction.triggered.connect(library.bookmarksManagerGUI.display)
        self.addAction(manageBookmarksAction)

        # Bookmarks manager! FINALLY! Yay!
        viewNotificationsAction = QtGui.QAction(tr('viewNotifications'), self)
        viewNotificationsAction.setShortcut("Ctrl+Alt+N")
        viewNotificationsAction.triggered.connect(notificationManager.show)
        self.addAction(viewNotificationsAction)

        # Tabs
        self.tabs = MovableTabWidget(self)
        self.tabs.currentChanged.connect(self.hideInspectors)
        self.tabs.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.tabs.setMovable(True)
        self.nextTabAction = QtGui.QAction(self)
        self.nextTabAction.triggered.connect(self.nextTab)
        self.nextTabAction.setShortcut("Ctrl+Tab")
        self.addAction(self.nextTabAction)
        self.previousTabAction = QtGui.QAction(self)
        self.previousTabAction.triggered.connect(self.previousTab)
        self.previousTabAction.setShortcut("Ctrl+Shift+Tab")
        self.addAction(self.previousTabAction)
        self.tabs.setTabsClosable(True)
        self.tabs.currentChanged.connect(self.updateTitles)
        self.tabs.tabCloseRequested.connect(self.closeTab)

        self.fullScreenAction = QtGui.QAction(tr("toggleFullscreen"), self)
        self.fullScreenAction.setShortcut("F11")
        self.fullScreenAction.triggered.connect(self.toggleFullScreen)
        self.addAction(self.fullScreenAction)

        self.rMaxAction = QtGui.QAction(self)
        self.rMaxAction.setShortcut("Alt+F10")
        self.rMaxAction.triggered.connect(self.rMax)
        self.addAction(self.rMaxAction)

        # "Toolbar" for top right corner
        self.cornerWidgets = QtGui.QWidget()
        self.cornerWidgets.setSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Preferred)
#        self.cornerWidgets.setStyleSheet(cornerWidgetsSheet)
        self.tabs.setCornerWidget(self.cornerWidgets,QtCore.Qt.TopRightCorner)
        self.cornerWidgetsLayout = QtGui.QHBoxLayout()
        self.cornerWidgetsLayout.setContentsMargins(0,0,0,0)
        self.cornerWidgetsLayout.setSpacing(0)
        self.cornerWidgets.setLayout(self.cornerWidgetsLayout)
        self.cornerWidgetsToolBar = QtGui.QToolBar()
        themet = ""
        if app_use_ambiance:
            themet = """ 
            QPushButton, QToolButton {
            color: #dfdbd2;
            }

            QPushButton:hover, QToolButton:hover {
            color: palette(button-text);
            }"""
        self.cornerWidgetsToolBar.setStyleSheet("QToolBar { border: 0; background: transparent; padding: 0; margin: 0; }" + themet)
        self.cornerWidgetsLayout.addWidget(self.cornerWidgetsToolBar)

        """self.showCornerWidgetsMenuAction = QtGui.QAction(self)
        self.showCornerWidgetsMenuAction.setShortcut("Alt+M")
        self.showCornerWidgetsMenuAction.setToolTip(tr("cornerWidgetsMenuTT"))
        self.showCornerWidgetsMenuAction.triggered.connect(self.showCornerWidgetsMenu)"""
        self.mainMenuButton = QtGui.QAction(self)
        self.mainMenuButton.setText(tr("menu"))
        self.mainMenuButton.setShortcuts(["Alt+M", "Alt+F", "Alt+E"])
        self.mainMenuButton.triggered.connect(self.showCornerWidgetsMenu)
#        self.mainMenuButton.setArrowType(QtCore.Qt.DownArrow)
        self.mainMenu = QtGui.QMenu(self)
        self.mainMenu.setTitle(tr('menu'))

        closeTabForeverAction = QtGui.QAction(tr('closeTabForever'), self)
        closeTabForeverAction.setShortcut("Ctrl+Shift+W")
        self.addAction(closeTabForeverAction)
        closeTabForeverAction.triggered.connect(self.permanentCloseTab)

        # New tab button
        newTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("tab-new", QtGui.QIcon(os.path.join(app_icons, 'newtab.png'))), tr('newTabBtn'), self)
        newTabAction.setToolTip(tr('newTabBtnTT'))
        newTabAction.setShortcuts(['Ctrl+T'])
        newTabAction.triggered.connect(self.newTab)
        self.addAction(newTabAction)
        self.newTabButton = QtGui.QToolButton()
        self.newTabButton.setFocusPolicy(QtCore.Qt.TabFocus)
        self.newTabButton.setDefaultAction(newTabAction)
        self.cornerWidgetsToolBar.addWidget(self.newTabButton)

        self.tabsContextMenuButton = QtGui.QAction(self)
        self.tabsContextMenuButton.setShortcuts(["Alt+V", "Alt+W", "Alt+T"])
        self.tabsContextMenuButton.triggered.connect(self.showTabsContextMenuAtCornerWidgets)
        self.cornerWidgetsToolBar.addAction(self.tabsContextMenuButton)
        self.cornerWidgetsToolBar.widgetForAction(self.tabsContextMenuButton).setArrowType(QtCore.Qt.DownArrow)
        self.cornerWidgetsToolBar.widgetForAction(self.tabsContextMenuButton).setFocusPolicy(QtCore.Qt.TabFocus)
        self.cornerWidgetsToolBar.widgetForAction(self.tabsContextMenuButton).setStyleSheet("QToolButton { max-width: 20px; }")

        # New window button
        newWindowAction = QtGui.QAction(QtGui.QIcon().fromTheme("window-new", QtGui.QIcon(os.path.join(app_icons, 'newwindow.png'))), tr("newWindowBtn"), self)
        newWindowAction.setShortcut('Ctrl+N')
        newWindowAction.triggered.connect(self.newWindow)
        self.addAction(newWindowAction)

        # Save page action
        savePageAction = QtGui.QAction(QtGui.QIcon().fromTheme("document-save-as", QtGui.QIcon(os.path.join(app_icons, 'saveas.png'))), tr('saveAs'), self)
        savePageAction.setShortcut('Ctrl+S')
        savePageAction.triggered.connect(self.savePage)
        self.mainMenu.addAction(savePageAction)
        self.addAction(savePageAction)

        printAction = QtGui.QAction(QtGui.QIcon().fromTheme("document-print", QtGui.QIcon(os.path.join(app_icons, 'print.png'))), tr('print'), self)
        printAction.setShortcut('Ctrl+P')
        printAction.triggered.connect(self.printPage)
        self.mainMenu.addAction(printAction)
        self.addAction(printAction)

        printPreviewAction = QtGui.QAction(QtGui.QIcon().fromTheme("document-print-preview", QtGui.QIcon(os.path.join(app_icons, 'printpreview.png'))), tr('printPreviewHKey'), self)
        printPreviewAction.triggered.connect(self.printPreview)
        self.mainMenu.addAction(printPreviewAction)
        self.addAction(printPreviewAction)

        self.mainMenu.addSeparator()

        self.mainMenu.addAction(self.fullScreenAction)

        self.mainMenu.addSeparator()

        # Undo closed tab button
        undoCloseTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("edit-undo", QtGui.QIcon(os.path.join(app_icons, 'undo.png'))), tr('undoCloseTabBtn'), self)
        undoCloseTabAction.setToolTip(tr('undoCloseTabBtnTT'))
        undoCloseTabAction.setShortcuts(['Ctrl+Shift+T'])
        undoCloseTabAction.triggered.connect(self.undoCloseTab)
        self.addAction(undoCloseTabAction)

        undoCloseWindowAction = QtGui.QAction(tr('undoCloseWindow'), self)
        undoCloseWindowAction.setShortcut("Ctrl+Shift+N")
        undoCloseWindowAction.triggered.connect(undoCloseWindow)
        self.addAction(undoCloseWindowAction)

        # History sidebar button
        historyToggleAction = QtGui.QAction(QtGui.QIcon.fromTheme("document-open-recent", QtGui.QIcon(os.path.join(app_icons, "history.png"))), tr('viewHistoryBtn'), self)
        historyToggleAction.setToolTip(tr('viewHistoryBtnTT'))
        historyToggleAction.triggered.connect(self.historyToggle)
        historyToggleAction.triggered.connect(self.historyToolBar.show)
        historyToggleAction.setShortcut("Ctrl+H")
        self.addAction(historyToggleAction)
        self.mainMenu.addAction(historyToggleAction)

        advHistoryAction = QtGui.QAction(tr('viewAdvHistory'), self)
        advHistoryAction.setShortcut("Ctrl+Shift+H")
        advHistoryAction.triggered.connect(library.advancedHistoryViewGUI.display)
        self.addAction(advHistoryAction)
        self.mainMenu.addAction(advHistoryAction)

        # New private browsing tab button
        newpbTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("face-devilish", QtGui.QIcon(os.path.join(app_icons, 'pb.png'))), tr('newPBTabBtn'), self)
        newpbTabAction.setToolTip(tr('newPBTabBtnTT'))
        newpbTabAction.setShortcuts(['Ctrl+Shift+P'])
        newpbTabAction.triggered.connect(self.newpbTab)
        self.addAction(newpbTabAction)
#        self.mainMenu.addAction(closeTabForeverAction)
        self.mainMenu.addSeparator()

        self.mainMenu.addAction(manageBookmarksAction)
        self.mainMenu.addSeparator()

        closeTabAction = QtGui.QAction(tr('closeTab'), self)
        closeTabAction.setShortcut("Ctrl+W")
        closeTabAction.triggered.connect(self.closeCurrentTab)
        self.addAction(closeTabAction)
        closeLeftTabsAction = QtGui.QAction(QtGui.QIcon(os.path.join(app_icons, 'close-left.png')), tr('closeLeftTabs'), self)
        closeLeftTabsAction.setShortcut("Ctrl+Shift+L")
        closeLeftTabsAction.triggered.connect(self.closeLeftTabs)
        self.addAction(closeLeftTabsAction)
        closeRightTabsAction = QtGui.QAction(QtGui.QIcon(os.path.join(app_icons, 'close-right.png')), tr('closeRighttTabs'), self)
        closeRightTabsAction.setShortcut("Ctrl+Shift+R")
        closeRightTabsAction.triggered.connect(self.closeRightTabs)
        self.addAction(closeRightTabsAction)

        self.tabsContextMenu = ContextMenu()
        self.tabsContextMenu.setTitle(tr("windowsHKey"))
        self.tabsContextMenu.addAction(newTabAction)
        self.tabsContextMenu.addAction(newWindowAction)
        self.tabsContextMenu.addAction(newpbTabAction)
        self.tabsContextMenu.addSeparator()
        self.tabsContextMenu.addAction(closeTabAction)
        self.tabsContextMenu.addAction(closeLeftTabsAction)
        self.tabsContextMenu.addAction(closeRightTabsAction)
        self.tabsContextMenu.addAction(closeTabForeverAction)
        self.tabsContextMenu.addSeparator()
        self.tabsContextMenu.addAction(undoCloseTabAction)
        self.tabsContextMenu.addAction(undoCloseWindowAction)

        self.menuBar = QtGui.QMenuBar()
        self.menuBar.addMenu(self.mainMenu)
        self.menuBar.addMenu(self.tabsContextMenu)
        self.setMenuBar(self.menuBar)
        self.menuBar.setVisible(False)

        self.tabs.customContextMenuRequested.connect(self.tabsContextMenu.show2)

        self.cornerWidgetsToolBar.addSeparator()

        self.cornerWidgetsToolBar.addAction(self.mainMenuButton)
        self.cornerWidgetsToolBar.widgetForAction(self.mainMenuButton).setFocusPolicy(QtCore.Qt.TabFocus)

        # Activate tab actions
        activateTab1Action = QtGui.QAction(self)
        activateTab2Action = QtGui.QAction(self)
        activateTab3Action = QtGui.QAction(self)
        activateTab4Action = QtGui.QAction(self)
        activateTab5Action = QtGui.QAction(self)
        activateTab6Action = QtGui.QAction(self)
        activateTab7Action = QtGui.QAction(self)
        activateTab8Action = QtGui.QAction(self)
        activateTab9Action = QtGui.QAction(self)
        numActions = [activateTab1Action, activateTab2Action, activateTab3Action, activateTab4Action, activateTab5Action, activateTab6Action, activateTab7Action, activateTab8Action, activateTab9Action]
        for action in range(len(numActions)):
            numActions[action].setShortcuts(["Ctrl+" + str(action + 1), "Alt+" + str(action + 1)])
            exec("numActions[action].triggered.connect(self.activateTab" + str(action + 1) + ")")
            self.addAction(numActions[action])

        # Config button
        configAction = QtGui.QAction(QtGui.QIcon().fromTheme("preferences-system", QtGui.QIcon(os.path.join(app_icons, 'settings.png'))), tr('preferencesButton'), self)
        configAction.setToolTip(tr('preferencesButtonTT'))
        configAction.setShortcuts(['Ctrl+Alt+P'])
        configAction.triggered.connect(self.showSettings)

        self.addAction(configAction)
        self.toolsMenu = QtGui.QMenu(tr("toolsHKey"))
        self.mainMenu.addMenu(self.toolsMenu)
        viewSourceAction = QtGui.QAction(tr("viewSource"), self)
        viewSourceAction.setShortcut("Ctrl+Alt+U")
        viewSourceAction.triggered.connect(self.viewSource)
        self.toolsMenu.addAction(viewSourceAction)

        inspectAction = QtGui.QAction(tr("webInspectorHKey"), self)
        inspectAction.setShortcut("F12")
        inspectAction.triggered.connect(self.inspect)
        self.toolsMenu.addAction(inspectAction)

        self.toolsMenu.addSeparator()
        self.toolsMenu.addAction(viewNotificationsAction)

        downloadsAction = QtGui.QAction(tr("downloadsHKey"), self)
        downloadsAction.setShortcuts(["Ctrl+Shift+Y", "Ctrl+J"])
        downloadsAction.triggered.connect(downloadManagerGUI.show)
        self.toolsMenu.addAction(downloadsAction)
        self.addAction(downloadsAction)

        self.toolsMenu.addAction(clearHistoryAction)
        self.toolsMenu.addAction(configAction)
        self.mainMenu.addSeparator()

        # About Actions
        aboutQtAction = QtGui.QAction(tr('aboutQtHKey'), self)
        aboutQtAction.triggered.connect(QtGui.QApplication.aboutQt)
        self.mainMenu.addAction(aboutQtAction)

        aboutAction = QtGui.QAction(tr('aboutRyoukoHKey'), self)
        aboutAction.triggered.connect(self.aboutRyoukoHKey)
        self.mainMenu.addAction(aboutAction)

        self.mainMenu.addSeparator()

        self.mainMenu.addAction(quitAction)

        self.setCentralWidget(self.tabs)
        if len(sys.argv) == 1:
            self.newTab()
            self.tabs.widget(self.tabs.currentIndex()).webView.buildNewTabPage()
        elif len(sys.argv) > 1:
            for arg in range(1, len(sys.argv)):
                if not "--pb" in sys.argv and not "-pb" in sys.argv:
                    try:
                        sys.argv[arg - 1]
                    except:
                        if not sys.argv[arg] == "-P":
                            self.newTab(sys.argv[arg])
                    else:
                        if not (sys.argv[arg - 1] == "-P") and not sys.argv[arg] == "-P":
                            self.newTab(sys.argv[arg])
                else:
                    try:
                        sys.argv[arg - 1]
                    except:
                        if not sys.argv[arg] == "-P" and not sys.argv[arg] == "--pb" and not sys.argv[arg] == "-pb":
                            self.newpbTab(sys.argv[arg])
                    else:
                        if not (sys.argv[arg - 1] == "-P") and not sys.argv[arg] == "-P" and not sys.argv[arg] == "--pb" and not sys.argv[arg] == "-pb":
                            self.newpbTab(sys.argv[arg])
            for arg in range(1, len(sys.argv)):
                del sys.argv[1]
            if self.tabs.count() == 0:
                self.newTab()
                self.tabs.widget(self.tabs.currentIndex()).webView.buildNewTabPage()

    def toggleFullScreen(self):
        if self.windowState() == QtCore.Qt.WindowFullScreen:
            self.setWindowState(QtCore.Qt.WindowNoState)
        else:
            self.setWindowState(QtCore.Qt.WindowFullScreen)

    def rMax(self):
        if self.windowState() == QtCore.Qt.WindowMaximized:
            self.setWindowState(QtCore.Qt.WindowNoState)
        else:
            self.setWindowState(QtCore.Qt.WindowMaximized)

    def viewSource(self):
        self.tabs.widget(self.tabs.currentIndex()).webView.viewSource()

    def inspect(self):
        self.tabs.widget(self.tabs.currentIndex()).webView.showInspector()

    def activateTab1(self):
        self.tabs.setCurrentIndex(0)

    def activateTab2(self):
        self.tabs.setCurrentIndex(1)

    def activateTab3(self):
        self.tabs.setCurrentIndex(2)

    def activateTab4(self):
        self.tabs.setCurrentIndex(3)

    def activateTab5(self):
        self.tabs.setCurrentIndex(4)

    def activateTab6(self):
        self.tabs.setCurrentIndex(5)

    def activateTab7(self):
        self.tabs.setCurrentIndex(6)

    def activateTab8(self):
        self.tabs.setCurrentIndex(7)

    def activateTab9(self):
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def savePage(self):
        self.tabs.widget(self.tabs.currentIndex()).webView.savePage()

    def printPage(self):
        self.tabs.widget(self.tabs.currentIndex()).webView.printPage()

    def printPreview(self):
        self.tabs.widget(self.tabs.currentIndex()).webView.printPreview()

    def hideInspectors(self):
        for tab in range(self.tabs.count()):
            try:
                self.tabs.widget(tab).webInspectorDock.hide()
            except:
                doNothing()

    def showTabsContextMenu(self):
        x = QtCore.QPoint(QtGui.QCursor.pos()).x()
        if x + self.tabsContextMenu.width() > QtGui.QApplication.desktop().size().width():
            x = x - self.tabsContextMenu.width()
        y = QtCore.QPoint(QtGui.QCursor.pos()).y()
        if y + self.tabsContextMenu.height() > QtGui.QApplication.desktop().size().height():
            y = y - self.tabsContextMenu.height()
        self.tabsContextMenu.move(x, y)
        self.tabsContextMenu.show2()

    def showTabsContextMenuAtCornerWidgets(self):
        x = self.cornerWidgetsToolBar.widgetForAction(self.tabsContextMenuButton).mapToGlobal(QtCore.QPoint(0,0)).x()
        y = self.cornerWidgetsToolBar.widgetForAction(self.tabsContextMenuButton).mapToGlobal(QtCore.QPoint(0,0)).y()
        width = self.cornerWidgetsToolBar.widgetForAction(self.tabsContextMenuButton).width()
        height = self.cornerWidgetsToolBar.widgetForAction(self.tabsContextMenuButton).height()
        self.tabsContextMenu.show()
        if x - self.tabsContextMenu.width() + width < 0:
            x = 0
        else:
            x = x - self.tabsContextMenu.width() + width
        if y + height + self.tabsContextMenu.height() >= QtGui.QApplication.desktop().size().height():
            y = y - self.tabsContextMenu.height()
        else:
            y = y + height
        self.tabsContextMenu.move(x, y)

    def showCornerWidgetsMenu(self):
        x = self.cornerWidgetsToolBar.widgetForAction(self.mainMenuButton).mapToGlobal(QtCore.QPoint(0,0)).x()
        y = self.cornerWidgetsToolBar.widgetForAction(self.mainMenuButton).mapToGlobal(QtCore.QPoint(0,0)).y()
        width = self.cornerWidgetsToolBar.widgetForAction(self.mainMenuButton).width()
        height = self.cornerWidgetsToolBar.widgetForAction(self.mainMenuButton).height()
        self.mainMenu.show()
        if x - self.mainMenu.width() + width < 0:
            x = 0
        else:
            x = x - self.mainMenu.width() + width
        if y + height + self.mainMenu.height() >= QtGui.QApplication.desktop().size().height():
            y = y - self.mainMenu.height()
        else:
            y = y + height
        self.mainMenu.move(x, y)

    def showSettings(self):
        cDialog.show()
        centerWidget(cDialog)

    def updateSettings(self):
        for tab in range(self.tabs.count()):
            self.tabs.widget(tab).updateSettings()

    def nextTab(self):
        tabIndex = self.tabs.currentIndex() + 1
        if tabIndex < self.tabs.count():
            self.tabs.setCurrentIndex(tabIndex)
        else:
            self.tabs.setCurrentIndex(0)
    def previousTab(self):
        tabIndex = self.tabs.currentIndex() - 1
        if tabIndex >= 0:
            self.tabs.setCurrentIndex(tabIndex)
        else:
            self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def newTab(self, url="about:blank"):
        if cDialog.settings['privateBrowsing']:
            self.newpbTab(url)
        else:
            self.tabCount += 1
            s = str(self.tabCount)
            if url != False:
                try:
                    exec("tab" + s + " = Browser(self, \"" + metaunquote(url) + "\")")
                except:
                    exec("tab" + s + " = Browser(self, \"" + url + "\")")
            else:
                exec("tab%s = Browser(self)" % (s))
            exec("tab%s.webView.titleChanged.connect(self.updateTitles)" % (s))
            exec("tab%s.webView.urlChanged.connect(self.reloadHistory)" % (s))
            exec("tab%s.webView.titleChanged.connect(self.reloadHistory)" % (s))
            exec("tab%s.webView.iconChanged.connect(self.updateIcons)" % (s))
            exec("self.tabs.addTab(tab" + s + ", tab" + s + ".webView.icon(), 'New Tab')")
            self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def newpbTab(self, url="about:blank"):
        self.tabCount += 1
        s = str(self.tabCount)
        if url != False:
            exec("tab" + s + " = Browser(self, '" + metaunquote(url) + "', True)")
        else:
            exec("tab" + s + " = Browser(self, 'about:blank', True)")
        exec("tab" + s + ".webView.titleChanged.connect(self.updateTitles)")
        exec("tab" + s + ".webView.urlChanged.connect(self.reloadHistory)")
        exec("tab" + s + ".webView.titleChanged.connect(self.reloadHistory)")
        exec("tab" + s + ".webView.iconChanged.connect(self.updateIcons)")
        exec("self.tabs.addTab(tab" + s + ", tab" + s + ".webView.icon(), 'New Tab')")
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def newWindow(self):
        if settingsManager.settings['oldSchoolWindows']:
            self.tabs.widget(self.tabs.currentIndex()).webView.newWindow()
        else:
            nwin = TabBrowser(self)
            nwin.show()

    def openHistoryItem(self, item):
        if self.searchOn == False:
            self.newTab(browserHistory.history[self.historyList.row(item)]['url'])
        else:
            self.newTab(self.tempHistory[self.historyList.row(item)]['url'])
    def reloadHistory(self):
        try:
            if self.searchOn == False:
                self.historyList.clear()
                browserHistory.reload()
                for item in browserHistory.history:
                    self.historyList.addItem(qstring(unicode(item['name'])))
            else:
                browserHistory.reload()
        except:
            browserHistory.reset()
    def searchHistory(self, string=""):
        string = unicode(string)
        if string != "":
            self.searchOn = True
            self.historyList.clear()
            history = []
            string = unicode(string)
            for item in browserHistory.history:
                add = False
                for subitem in item:
                    if string.lower() in unicode(item[subitem]).lower():
                        add = True
                        break
                if add == True:
                    history.append(item)
                    self.historyList.addItem(item['name'])
            self.tempHistory = history
        else:
            self.searchOn = False
            self.reloadHistory()
    def deleteHistoryItem(self):
        if self.historyList.hasFocus():
            browserHistory.removeByName(unicode(self.historyList.currentItem().text()))

    def showClearHistoryDialog(self):
        clearHistoryDialog.display()

    def historyToggle(self):
        self.historyDock.setVisible(not self.historyDock.isVisible())
        if self.historyDock.isVisible():
            self.focusHistorySearch()
    def focusHistorySearch(self):
        self.searchHistoryField.setFocus()
        self.searchHistoryField.selectAll()

    def closeCurrentTab(self):
        self.closeTab(self.tabs.currentIndex())

    def closeTab(self, index=None, permanent=False):
        if index == None:
            index = self.tabs.currentIndex()
        if self.tabs.count() > 0:
            if (self.tabs.widget(index).webView.pb) or (unicode(self.tabs.widget(index).webView.url().toString()) == "" or unicode(self.tabs.widget(index).webView.url().toString()) == "about:blank") or permanent==True:
                self.tabs.widget(index).deleteLater()
            else:
                self.closedTabList.append({'widget' : self.tabs.widget(index), 'title' : unicode(self.tabs.widget(index).webView.title()), 'url' : unicode(self.tabs.widget(index).webView.url().toString())})
                self.tabs.widget(index).webView.load(QtCore.QUrl("about:blank"))
            self.tabs.removeTab(index)
            try: settingsManager.settings['maxUndoCloseTab']
            except:
                doNothing()
            else:
                if settingsManager.settings['maxUndoCloseTab'] >= 0:
                    if len(self.closedTabList) >= int(settingsManager.settings['maxUndoCloseTab'] + 1):
                        self.closedTabList[0]["widget"].deleteLater()
                        del self.closedTabList[0]
            if self.tabs.count() == 0:
                self.close()

    def permanentCloseTab(self):
        self.closeTab(self.tabs.currentIndex(), True)

    def closeLeftTabs(self):
        t = self.tabs.currentIndex()
        self.tabs.setCurrentIndex(0)
        for i in range(t):
            self.closeTab(0)

    def closeRightTabs(self):
        while self.tabs.currentIndex() != self.tabs.count() - 1:
            self.closeTab(self.tabs.count() - 1)

    def undoCloseTab(self, index=False):
        if len(self.closedTabList) > 0:
            self.tabs.addTab(self.closedTabList[len(self.closedTabList) - 1]['widget'], self.closedTabList[len(self.closedTabList) - 1]['widget'].webView.icon(), self.closedTabList[len(self.closedTabList) - 1]['widget'].webView.title())
            del self.closedTabList[len(self.closedTabList) - 1]
            self.updateTitles()
            self.tabs.setCurrentIndex(self.tabs.count() - 1)
            if self.tabs.widget(self.tabs.currentIndex()).webView.url().toString() == "about:blank":
                self.tabs.widget(self.tabs.currentIndex()).webView.back()

    def updateIcons(self):
        for tab in range(self.tabs.count()):
            i = self.tabs.widget(tab).webView.icon()
            if i.actualSize(QtCore.QSize(16, 16)).width() > 0:
                self.tabs.setTabIcon(tab, self.tabs.widget(tab).webView.icon())
            else:
                self.tabs.setTabIcon(tab, app_webview_default_icon)

    def updateTitles(self):
        for tab in range(self.tabs.count()):
            if unicode(self.tabs.widget(tab).webView.title()) == "":
                if not self.tabs.widget(tab).pb:
                    self.tabs.setTabText(tab, tr('newTab'))
                else:
                    self.tabs.setTabText(tab, tr('newPBTab'))
                if tab == self.tabs.currentIndex():
                    self.setWindowTitle("Ryouko")
                self.tabs.setTabIcon(tab, app_webview_default_icon)                    
            else:
                if len(unicode(self.tabs.widget(tab).webView.title())) > 20:
                    title = ""
                    chars = 0
                    for char in unicode(self.tabs.widget(tab).webView.title()):
                        title += char
                        chars += 1
                        if chars >= 19:
                            title = "%s..." % (title)
                            break
                    title = qstring(title)
                else:
                    title = self.tabs.widget(tab).webView.title()
                if self.tabs.widget(tab).pb:
                    title = unicode(title)
                    title = "%s (PB)" % (title)
                    title = qstring(title)
                self.tabs.setTabText(tab, title)
                if tab == self.tabs.currentIndex():
                    self.setWindowTitle("%s - Ryouko" % (unicode(self.tabs.widget(tab).webView.title())))

win = None

class Ryouko(QtGui.QWidget):
    def __init__(self):
        dA = QtWebKit.QWebPage()
        dA.mainFrame().setHtml("<html><body><span id='userAgent'></span></body></html>")
        dA.mainFrame().evaluateJavaScript("document.getElementById(\"userAgent\").innerHTML = navigator.userAgent;")
        global app_default_useragent
        app_default_useragent = unicode(dA.mainFrame().findFirstElement("#userAgent").toPlainText()).replace("Safari", "Ryouko/" + app_version + " Safari")
        dA.deleteLater()
        del dA
        q = QtWebKit.QWebView()
        q.load(QtCore.QUrl("about:blank"))
        global app_webview_default_icon
        app_webview_default_icon = QtGui.QIcon(q.icon())
        q.deleteLater()
        del q
        if not os.path.isdir(app_profile):
            os.makedirs(app_profile)
        if not os.path.isdir(os.path.join(app_profile, "temp")):
            os.mkdir(os.path.join(app_profile, "temp"))
        if not os.path.isdir(os.path.join(app_profile, "adblock")):
            os.mkdir(os.path.join(app_profile, "adblock"))
        try:
            settingsManager.loadSettings()
            try: settingsManager.settings['cloudService']
            except:
                doNothing()
            else:
                if settingsManager.settings['cloudService'] != "No":
                    bck = os.path.join(os.path.expanduser("~"), settingsManager.settings['cloudService'], "ryouko-profiles", app_profile_name)
                    a = ""
                    for char in settingsManager.settings['cloudService']:
                        a = a + char
                    changeProfile(bck)
                    loadCookies()
                    searchManager.changeProfile(app_profile)
                    browserHistory.setAppProfile(app_profile)
                    browserHistory.reload()
                    settingsManager.changeProfile(app_profile)
                    settingsManager.settings['cloudService'] = a
                    settingsManager.saveSettings()
        except:
            doNothing()
        if os.path.exists(app_lock) and not sys.platform.startswith("win"):
            reply = QtGui.QMessageBox.question(None, tr("error"),
        tr("isRunning"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Yes:
                f = open(app_instance2, "w")
                f.write("")
                f.close()
                f = open(app_instance2, "a")
                for arg in range(1, len(sys.argv)):
                    if not sys.argv[arg].lower() == "--pb" and not sys.argv[arg].lower() == "-pb" and not sys.argv[arg] == "-P":
                        f.write("%s\n" % (sys.argv[arg]))
                f.close()
            else:
                if os.path.exists(app_lock):
                    os.remove(app_lock)
                args = ""
                for arg in sys.argv:
                    args = "%s%s " % (args, arg)
                os.system("%s && echo \"\"" % (args))
            QtCore.QCoreApplication.instance().quit()
            sys.exit()
        if not os.path.isdir(app_profile):
            os.makedirs(app_profile)
        if not os.path.isdir(os.path.join(app_profile, "temp")):
            os.mkdir(os.path.join(app_profile, "temp"))
        if not os.path.isdir(os.path.join(app_profile, "adblock")):
            os.mkdir(os.path.join(app_profile, "adblock"))
        loadCookies()
        global library
        global searchEditor
        global cDialog
        global win
        global aboutDialog
        global notificationManager
        global clearHistoryDialog
        global downloadManagerGUI
        downloadManagerGUI = DownloadManagerGUI()
        downloadManagerGUI.networkAccessManager.setCookieJar(app_cookiejar)
        app_cookiejar.setParent(QtCore.QCoreApplication.instance())
        downloadManagerGUI.downloadFinished.connect(downloadFinished)
        aboutDialog = RAboutDialog()
        notificationManager = NotificationManager()
        clearHistoryDialog = ClearHistoryDialog()
        library = Library()
        searchEditor = SearchEditor()
        cDialog = CDialog(self)
        win = TabBrowser(self)
    def primeBrowser(self):
        global win
        win.show()
#        if app_profile_exists == True:
#            notificationMessage(tr("profileError"))

def updateProgress(pr):
    global app_launcher
    if pr != 0.0:
        app_launcher.set_property("progress_visible", True)
        app_launcher.set_property("progress", pr)
    else:
        app_launcher.set_property("progress_visible", False)

def main():
    if "--help" in sys.argv or "-h" in sys.argv:
        print(tr("help"))
    if "--icons" in sys.argv:
        print(app_icons)
    else:
        if "-P" in sys.argv:
            try:
                i = sys.argv.index("-P")
            except:
                doNothing()
            else:
                try:
                    sys.argv[i + 1]
                except:
                    doNothing()
                else:
                    changeProfile(os.path.join(app_profile_folder, sys.argv[i + 1]))
        if os.path.exists(app_lock) and sys.platform.startswith("win"):
            app = QtGui.QApplication(sys.argv)
            reply = QtGui.QMessageBox.question(None, tr("error"),
        tr("isRunning"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.Yes)
            if reply == QtGui.QMessageBox.Yes:
                f = open(app_instance2, "w")
                f.write("")
                f.close()
                f = open(app_instance2, "a")
                for arg in range(1, len(sys.argv)):
                    if not sys.argv[arg].lower() == "--pb" and not sys.argv[arg].lower() == "-pb" and not sys.argv[arg] == "-P":
                        f.write("%s\n" % (sys.argv[arg]))
                f.close()
            else:
                os.remove(app_lock)
                args = ""
                for arg in sys.argv:
                    args = "%s%s " % (args, arg)
                os.system("%s && echo \"\"" % (args))
            QtCore.QCoreApplication.instance().quit()
            sys.exit()
        else:
            global user_links
            user_links = reload_user_links(app_links)
            global reset
            app = QtGui.QApplication(sys.argv)
            app.aboutToQuit.connect(prepareQuit)
            if reset == True:
                browserHistory.reset()
                reset = False
            ryouko = Ryouko()
            ryouko.primeBrowser()
            f = open(app_lock, "w")
            f.write("")
            f.close()
            if use_unity_launcher == True:
                loop = GObject.MainLoop()
                global app_launcher
                app_launcher = Unity.LauncherEntry.get_for_desktop_id("ryouko.desktop")
                downloadManagerGUI.downloadProgress.connect(updateProgress)
            app.exec_()

if __name__ == "__main__":
    main()
