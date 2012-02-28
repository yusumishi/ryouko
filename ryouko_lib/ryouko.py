#! /usr/bin/env python

from __future__ import print_function

import os, sys, pickle, json, time, datetime
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork, uic
try: from urllib.request import urlretrieve
except ImportError:
    try: from urllib import urlretrieve
    except:
        print("", end="")

app_lib = os.path.dirname(os.path.realpath(__file__))
app_home = os.path.expanduser(os.path.join("~", ".ryouko-data"))

def doNothing():
    return

def qstring(string):
    if sys.version_info[0] <= 2:
        return(QtCore.QString(string))
    else:
        return(string)

if sys.version_info[0] >= 3:
    def unicode(data):
        return str(data)

def message(content="This is a message.", title="Alert", icon="info"):
    message = QtGui.QMessageBox()
    message.setWindowTitle(title)
    message.setText(qstring(str(content)))
    message.addButton(QtGui.QMessageBox.Ok)
    if str(icon).lower() == "info" or str(icon).lower() == "information":
        message.setIcon(QtGui.QMessageBox.Information)
    elif str(icon).lower() == "warn" or str(icon).lower() == "warning":
        message.setIcon(QtGui.QMessageBox.Warning)
    elif str(icon).lower() == "critical":
        message.setIcon(QtGui.QMessageBox.Question)
    elif str(icon).lower() == "query" or str(icon).lower() == "question":
        message.setIcon(QtGui.QMessageBox.Question)
    elif str(icon).lower() == "query" or str(icon).lower() == "question":
        message.setIcon(QtGui.QMessageBox.Question)
    elif str(icon).lower() == "none" or str(icon).lower() == "noicon":
        message.setIcon(QtGui.QMessageBox.NoIcon)
    else:
        message.setIcon(QtGui.QMessageBox.Information)
    message.exec_()

def inputBox(self, content="Enter a value here:", title="Query", value=""):
    text = QtGui.QInputDialog.getText(content, title, value)
    if text:
        text = str(text)
        return text[0]

class BrowserHistory():
    def __init__(self):
        self.history = []
        self.url = "about:blank"
        self.ryouko_home = app_home
        if not os.path.exists(os.path.join(self.ryouko_home, "history.json")):
            self.save()
        self.reload()
    def reload(self):
        if os.path.exists(os.path.join(self.ryouko_home, "history.json")):
            history = open(os.path.join(self.ryouko_home, "history.json"), "r")
            self.history = json.load(history)
            history.close()
    def save(self):
        history = open(os.path.join(self.ryouko_home, "history.json"), "w")
        json.dump(self.history, history)
        history.close()
    def append(self, url, name=""):
        self.reload()
        self.url = str(url.toString())
        url = str(url.toString())
        if url != "about:blank":
            now = datetime.datetime.now()
            add = True
            index = 0
            count = 1
            for item in self.history:
                if item[0].lower() == url:
                    add = False
                    index = self.history.index(item)
                    break
            if add == True:
                self.history.insert(0, [url, name, count, time.time(), time.strftime("%A"), time.strftime("%B"), time.strftime("%d"), "%d" % now.year, time.strftime("%H:%M:%S")])
            else:
                if len(self.history[index]) < 3:
                    self.history[index].append[1]
                if not type(self.history[index][2]) is int:
                    self.history[index][2] = 1
                count = self.history[index][2] + 1
                self.history[index][2] = count
                self.history[index][3] = time.time()
                tempIndex = self.history[index]
                del self.history[index]
                self.history.insert(0, tempIndex)
        self.save()
    def updateTitles(self, title):
        self.reload()
        title = str(title)
        for item in self.history:
            if item[0].lower() == self.url.lower():
                item[1] = title
        self.save()
    def removeByName(self, name=""):
        self.reload()
        for item in self.history:
            if item[1].lower() == name.lower():
                del item
        self.save()
    def removeByUrl(self, url=""):
        self.reload()
        for item in self.history:
            if item[0].lower() == url.lower():
                del item
        self.save()

class DownloaderThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.url = ""
        self.destination = ""
    def setUrl(self, url):
        self.url = url
    def setDestination(self, destination):
        self.destination = destination
    def exec_(self):
        urlretrieve(self.url, self.destination)
    def run(self):
        urlretrieve(self.url, self.destination)

downloaderThread = DownloaderThread()

class RWebView(QtWebKit.QWebView):
    createNewWindow = QtCore.pyqtSignal(QtWebKit.QWebPage.WebWindowType)
    newWindows = [0]
    def __init__(self, parent=None):
        super(RWebView, self).__init__()
        self.parent = parent
        self.page().networkAccessManager().setCookieJar(self.parent.cookies)
        self.ryouko_home = app_home
        self.titleChanged.connect(self.updateTitle)
        if os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "logo.svg")):
            self.setWindowIcon(QtGui.QIcon(os.path.join(app_lib, "icons", "logo.svg")))
        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.downloadFile)
        self.page().downloadRequested.connect(self.downloadFile)
    def saveDialog(self, fname="", filters = "All files (*)"):
        saveDialog = QtGui.QFileDialog.getSaveFileName(None, "Save As", os.path.join(os.getcwd(), fname), filters)
        return saveDialog
    def downloadFile(self, request):
        fname = self.saveDialog(os.path.split(unicode(request.url().toString()))[1])
        if fname:
            downloaderThread.setUrl(unicode(request.url().toString()))
            downloaderThread.setDestination(fname)
            downloaderThread.start()
    def updateTitle(self):
        self.setWindowTitle(self.title())
    def createWindow(self, windowType):
        exec("self.newWindow" + str(len(self.newWindows)) + " = RWebView(self.parent)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction = QtGui.QAction(self.newWindow" + str(len(self.newWindows)) + ")")
        exec("self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction.setShortcut('Ctrl+W')")
        exec("self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction.triggered.connect(self.newWindow" + str(len(self.newWindows)) + ".close)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".addAction(self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".show()")
        exec("self.newWindows.append(self.newWindow" + str(len(self.newWindows)) + ")")
        self.createNewWindow.emit(windowType)
        return self.newWindows[len(self.newWindows) - 1]

class Browser(QtGui.QMainWindow):
    def __init__(self, parent=None, url=False):
        super(Browser, self).__init__()
        self.parent = parent
        self.ryouko_home = app_home
        self.tempHistory = []
        if not os.path.exists(self.ryouko_home):
            os.mkdir(self.ryouko_home)
        self.browserHistory = BrowserHistory()
        self.app_lib = app_lib
        self.version = "N/A"
        self.codename = "N/A"
        if os.path.exists(os.path.join(self.app_lib, "info.txt")):
            readVersionFile = open(os.path.join(self.app_lib, "info.txt"))
            metadata = readVersionFile.readlines()
            readVersionFile.close()
            if len(metadata) > 0:
                self.version = metadata[0].rstrip("\n")
            if len(metadata) > 1:
                self.codename = metadata[1].rstrip("\n")
        self.initUI(url)
    def initUI(self, url):
        uic.loadUi(os.path.join(self.app_lib, "mainwindow.ui"), self)
        self.webView = RWebView(self.parent)
        self.mainLayout.addWidget(self.webView, 2, 0)
        self.historyCompletion = QtGui.QListWidget()
        self.historyCompletion.itemActivated.connect(self.openHistoryItem)
        self.mainLayout.addWidget(self.historyCompletion, 3, 0)
        self.progressBar.hide()
        self.mainLayout.setSpacing(0);
        self.mainLayout.setContentsMargins(0, 0, 0, 0)
        self.mainToolBarLayout.setSpacing(0)
        self.goButton.clicked.connect(self.updateWeb)
        self.goButton.setText("")
        self.goButton.setIconSize(QtCore.QSize(16, 16))
        self.goButton.setIcon(QtGui.QIcon().fromTheme("go-jump", QtGui.QIcon(os.path.join(app_lib, "icons", 'go.png'))))
        self.goButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.backButton.clicked.connect(self.webView.back)
        self.backButton.setShortcut("Alt+Left")
        self.backButton.setIcon(QtGui.QIcon().fromTheme("go-previous", QtGui.QIcon(os.path.join(app_lib, "icons", 'back.png'))))
        self.backButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.nextButton.clicked.connect(self.webView.forward)
        self.nextButton.setText("")
        self.nextButton.setShortcut("Alt+Right")
        self.nextButton.setIcon(QtGui.QIcon().fromTheme("go-next", QtGui.QIcon(os.path.join(app_lib, "icons", 'next.png'))))
        self.nextButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.urlBar.returnPressed.connect(self.updateWeb)
        self.urlBar.textChanged.connect(self.searchHistory)
        self.webView.urlChanged.connect(self.updateText)
        self.webView.urlChanged.connect(self.browserHistory.append)
        self.webView.titleChanged.connect(self.browserHistory.updateTitles)
        self.searchButton.clicked.connect(self.searchWeb)
        self.searchButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.historyToggleToolBar = QtGui.QToolBar()
        self.historyToggleToolBar.setStyleSheet("""
        QToolBar {
        border-top: 0;
        background: transparent;
        }
        """)
        self.mainToolBarLayout.addWidget(self.historyToggleToolBar)
        historyToggleAction = QtGui.QAction(QtGui.QIcon.fromTheme("document-open-recent", QtGui.QIcon(os.path.join(self.app_lib, "icons", "history.png"))), "Toggle History Sidebar", self)
        historyToggleAction.setToolTip("<b>View History</b><br>Ctrl+H")
        self.historyToggleToolBar.addAction(historyToggleAction)
        historyToggleAction.triggered.connect(self.parent.historyToggle)
        historyToggleAction.triggered.connect(self.parent.historyToolBar.show)
        historyToggleAction.setShortcut("Ctrl+H")
        self.addAction(historyToggleAction)
        historySearchAction = QtGui.QAction(self)
        historySearchAction.triggered.connect(self.parent.focusHistorySearch)
        historySearchAction.setShortcuts(["Ctrl+Shift+K", "Ctrl+Shift+H"])
        self.addAction(historySearchAction)
        self.reloadButton.clicked.connect(self.webView.reload)
        self.reloadButton.setText("")
        self.reloadButton.setShortcut("F5")
        self.reloadButton.setIcon(QtGui.QIcon().fromTheme("view-refresh", QtGui.QIcon(os.path.join(app_lib, "icons", 'reload.png'))))
        self.reloadButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.reloadAction = QtGui.QAction(self)
        self.reloadAction.triggered.connect(self.webView.reload)
        self.reloadAction.setShortcut("Ctrl+R")
        self.addAction(self.reloadAction)
        self.stopButton.clicked.connect(self.webView.stop)
        self.stopButton.clicked.connect(self.historyCompletion.hide)
        self.stopButton.setText("")
        self.stopButton.setShortcut("Esc")
        self.stopButton.setIcon(QtGui.QIcon().fromTheme("process-stop", QtGui.QIcon(os.path.join(app_lib, "icons", 'stop.png'))))
        self.stopButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.focusURLBarButton.clicked.connect(self.focusURLBar)
        self.focusURLBarButton.setStyleSheet("""
        max-width: 0;
        min-width: 0;
        width: 0;
        border: 0;
        background: transparent;
        """)
        self.focusURLBarButton.setShortcut("Alt+D")
        self.focusURLBarButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.focusURLBarAction = QtGui.QAction(self)
        self.focusURLBarAction.setShortcut("Ctrl+L")
        self.focusURLBarAction.triggered.connect(self.focusURLBar)
        self.addAction(self.focusURLBarAction)
        self.stopButton.clicked.connect(self.updateText)
        self.webView.settings().setIconDatabasePath(qstring(self.ryouko_home))
        self.webView.loadFinished.connect(self.progressBar.hide)
        self.webView.loadProgress.connect(self.progressBar.setValue)
        self.webView.loadProgress.connect(self.progressBar.show)
        if url != False:
            self.urlBar.setText(qstring(url))
            self.updateWeb()
        elif len(sys.argv) > 1 and __name__ == "__main__":
            self.urlBar.setText(qstring(sys.argv[1]))
            self.updateWeb()
        self.updateText()
        self.historyCompletion.hide()
        self.webView.show()
    def searchHistory(self, string):
        string = str(string)
        if string != "" and string != str(self.webView.url().toString()) and string != "about:version":
            self.searchOn = True
            self.historyCompletion.clear()
            history = []
            string = str(string)
            for item in self.browserHistory.history:
                add = False
                for subitem in item:
                    if string.lower() in str(subitem).lower():
                        add = True
                if add == True:
                    history.append(item)
                    self.historyCompletion.addItem(item[1])
            self.tempHistory = history
            self.historyCompletion.show()
            self.webView.hide()
        else:
            self.historyCompletion.hide()
            self.webView.show()
    def openHistoryItem(self, item):
        self.webView.load(QtCore.QUrl(self.tempHistory[self.historyCompletion.row(item)][0]))
        self.historyCompletion.hide()
        self.webView.show()
    def licensing(self):
        url = QtCore.QUrl(os.path.join(self.app_lib, "LICENSE.html"))
        self.webView.load(url);
    def searchWeb(self):
        urlBar = self.urlBar.text()
        url = QtCore.QUrl("http://duckduckgo.com/?q=" + urlBar)
        self.webView.load(url)
    def focusURLBar(self):
        self.urlBar.setFocus()
        self.urlBar.selectAll()
    def updateWeb(self):
        urlBar = self.urlBar.text()
        header = ""
        if not str(urlBar).startswith("about:") and not str(urlBar).startswith("http://") and not str(urlBar).startswith("https://") and not str(urlBar).startswith("ftp://") and not str(urlBar).startswith("file://"):
            header = "http://"
        url = qstring(header + str(urlBar))
        if str(urlBar) == "about:" or str(urlBar) == "about:version":
            self.webView.setHtml("<html><head><title>About Ryouko</title></head><body style='font-family: sans-serif;'><center><h1 style='margin-bottom: 0;'>About Ryouko</h1><img src='file://" + os.path.join(app_lib, "icons", "about-logo.png") + "'></img><br><b>Ryouko version:</b> "+self.version+"<br><b>Release series:</b> \""+self.codename+"\"<br><b>Python version:</b> "+str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])+"<br><b>Qt version:</b> "+QtCore.qVersion()+"<br></center></body></html>")
        else:
            url = QtCore.QUrl(url)
            self.webView.load(url)
    def updateText(self):
        url = self.webView.url()
        texturl = url.toString()
        self.urlBar.setText(texturl)

class TabBrowser(QtGui.QMainWindow):
    def __init__(self):
        super(TabBrowser, self).__init__()
        if sys.version_info[0] >= 3:
            self.cookieFile = os.path.join(app_home, "cookies.pkl")
        else:
            self.cookieFile = os.path.join(app_home, "cookies-py2.pkl")
        self.tabCount = 0
        self.killCookies = False
        self.closedTabList = []
        self.ryouko_home = app_home
        if not os.path.exists(self.ryouko_home):
            os.mkdir(self.ryouko_home)
        self.searchOn = False
        self.app_lib = app_lib
        self.tempHistory = []

        self.cookies = QtNetwork.QNetworkCookieJar(QtCore.QCoreApplication.instance())
        cookies = []
        for c in self.loadCookies():
            cookies.append(QtNetwork.QNetworkCookie().parseCookies(c)[0])
        self.cookies.setAllCookies(cookies)

        self.initUI()

    def saveCookies(self):
        if self.killCookies == False:
            cookieFile = open(self.cookieFile, "wb")
            cookies = []
            for c in self.cookies.allCookies():
                cookies.append(c.toRawForm())
            pickle.dump(cookies, cookieFile)
            cookieFile.close()
        else:
            try: os.remove(self.cookieFile)
            except:
                doNothing()

    def loadCookies(self):
        if os.path.exists(self.cookieFile):
            cookieFile = open(self.cookieFile, "rb")
            cookies = []
            try: cookies = pickle.load(cookieFile)
            except:
                print("Error! Cookies could not be loaded!")
            else:
                doNothing()
            cookieFile.close()
            return cookies
        else:
            return []

    def closeEvent(self, ev):
        self.saveCookies()
        return QtGui.QMainWindow.closeEvent(self, ev)

    def createClearHistoryDialog(self):
        self.clearHistoryToolBar = QtGui.QToolBar("Clear History Dialog Toolbar")
        self.clearHistoryToolBar.setMovable(False)
        self.historyDockWindow.addToolBarBreak()
        self.historyDockWindow.addToolBar(self.clearHistoryToolBar)
        self.clearHistoryToolBar.hide()
        self.selectRange = QtGui.QComboBox()
        self.selectRange.addItem("Last minute")
        self.selectRange.addItem("Last 2 minutes")
        self.selectRange.addItem("Last 5 minutes")
        self.selectRange.addItem("Last 10 minutes")
        self.selectRange.addItem("Last 15 minutes")
        self.selectRange.addItem("Last 30 minutes")
        self.selectRange.addItem("Last hour")
        self.selectRange.addItem("Last 2 hours")
        self.selectRange.addItem("Last 4 hours")
        self.selectRange.addItem("Last 8 hours")
        self.selectRange.addItem("Last 24 hours")
        self.selectRange.addItem("Today")
        self.selectRange.addItem("Everything")
        self.selectRange.addItem("----------------")
        self.selectRange.addItem("Cookies")
        self.clearHistoryToolBar.addWidget(self.selectRange)
        self.clearHistoryButton = QtGui.QPushButton("Clear")
        self.clearHistoryButton.clicked.connect(self.clearHistory)
        self.clearHistoryToolBar.addWidget(self.clearHistoryButton)

    def initUI(self):
        self.setStyleSheet("""
        QListWidget {
        border: 0;
        }
        
        QToolButton, QPushButton {
        min-width: 24px;
        border: 1px solid transparent;
        padding: 2px;
        border-radius: 4px;
        background-color: transparent;
        }

        QToolButton:hover, QPushButton:hover {
        border: 1px solid palette(shadow);
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(light), stop:1 palette(button));
        }

        QToolButton:pressed, QPushButton:pressed {
        border: 1px solid palette(shadow);
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(shadow), stop:1 palette(button));
        }
        """)
        self.browserHistory = BrowserHistory()
        self.historyDock = QtGui.QDockWidget("History")
        self.historyDock.setFeatures(QtGui.QDockWidget.DockWidgetClosable)
        self.historyDockWindow = QtGui.QMainWindow()
        self.historyToolBar = QtGui.QToolBar("History Toolbar")
        self.historyToolBar.setMovable(False)
        self.historyList = QtGui.QListWidget()
        self.historyList.itemActivated.connect(self.openHistoryItem)
        deleteHistoryItemAction = QtGui.QAction(self)
        deleteHistoryItemAction.setShortcut("Del")
        deleteHistoryItemAction.triggered.connect(self.deleteHistoryItem)
        self.addAction(deleteHistoryItemAction)
        self.searchHistoryField = QtGui.QLineEdit()
        self.searchHistoryField.textChanged.connect(self.searchHistory)
        clearHistoryAction = QtGui.QAction(QtGui.QIcon.fromTheme("edit-clear", QtGui.QIcon(os.path.join(self.app_lib, "icons", "clear.png"))), "Clear History", self)
        clearHistoryAction.setShortcut("Ctrl+Shift+Del")
        clearHistoryAction.triggered.connect(self.showClearHistoryDialog)
        clearHistoryAction.triggered.connect(self.historyDock.show)
        self.addAction(clearHistoryAction)
        self.historyToolBar.addWidget(self.searchHistoryField)
        self.historyToolBar.addAction(clearHistoryAction)
        self.historyDockWindow.addToolBar(self.historyToolBar)
        self.createClearHistoryDialog()
        self.historyDockWindow.setCentralWidget(self.historyList)
        self.historyDock.setWidget(self.historyDockWindow)
        self.reloadHistory()
        self.addDockWidget(QtCore.Qt.LeftDockWidgetArea, self.historyDock)
        self.historyDock.hide()
        self.tabs = QtGui.QTabWidget()
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
        newTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("tab-new", QtGui.QIcon(os.path.join(os.path.dirname( os.path.realpath(__file__) ), 'add.png'))), '&New Tab', self)
        newTabAction.setShortcuts(['Ctrl+T'])
        newTabAction.triggered.connect(self.newTab)
        self.addAction(newTabAction)
        self.newTabButton = QtGui.QToolButton()
        self.newTabButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.newTabButton.setDefaultAction(newTabAction)
        self.tabs.setCornerWidget(self.newTabButton,QtCore.Qt.TopRightCorner)
        undoCloseTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("user-trash-full", QtGui.QIcon(os.path.join(os.path.dirname( os.path.realpath(__file__) ), 'trash.png'))), '&Undo Close Tab', self)
        undoCloseTabAction.setShortcuts(['Ctrl+Shift+T'])
        undoCloseTabAction.triggered.connect(self.undoCloseTab)
        self.addAction(undoCloseTabAction)
        self.undoCloseTabButton = QtGui.QToolButton()
        self.undoCloseTabButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.undoCloseTabButton.setDefaultAction(undoCloseTabAction)
        self.tabs.setCornerWidget(self.undoCloseTabButton,QtCore.Qt.TopLeftCorner)
        closeTabAction = QtGui.QAction(self)
        closeTabAction.setShortcuts(['Ctrl+W'])
        closeTabAction.triggered.connect(self.closeTab)
        self.addAction(closeTabAction)
        self.setCentralWidget(self.tabs)
        if len(sys.argv) == 1:
            self.newTab()
        elif len(sys.argv) > 1:
            for arg in range(1, len(sys.argv)):
                self.newTab(sys.argv[arg])
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
        self.tabCount += 1
        if url != False:
            exec("tab" + str(self.tabCount) + " = Browser(self, '"+str(url)+"')")
        else:
            exec("tab" + str(self.tabCount) + " = Browser(self)")
        exec("tab" + str(self.tabCount) + ".webView.titleChanged.connect(self.updateTitles)")
        exec("tab" + str(self.tabCount) + ".webView.urlChanged.connect(self.reloadHistory)")
        exec("tab" + str(self.tabCount) + ".webView.titleChanged.connect(self.reloadHistory)")
        exec("tab" + str(self.tabCount) + ".webView.iconChanged.connect(self.updateIcons)")
        exec("self.tabs.addTab(tab" + str(self.tabCount) + ", tab" + str(self.tabCount) + ".webView.icon(), 'New Tab')")
        self.tabs.setCurrentIndex(self.tabs.count() - 1)
    def openHistoryItem(self, item):
        if self.searchOn == False:
            self.newTab(self.browserHistory.history[self.historyList.row(item)][0])
        else:
            self.newTab(self.tempHistory[self.historyList.row(item)][0])
    def reloadHistory(self):
        if self.searchOn == False:
            self.historyList.clear()
            self.browserHistory.reload()
            for item in self.browserHistory.history:
                self.historyList.addItem(qstring(str(item[1])))
        else:
            self.browserHistory.reload()
    def searchHistory(self, string=""):
        string = str(string)
        if string != "":
            self.searchOn = True
            self.historyList.clear()
            history = []
            string = str(string)
            for item in self.browserHistory.history:
                add = False
                for subitem in item:
                    if string.lower() in str(subitem).lower():
                        add = True
                if add == True:
                    history.append(item)
                    self.historyList.addItem(item[1])
            self.tempHistory = history
        else:
            self.searchOn = False
            self.reloadHistory()
    def deleteHistoryItem(self):
        if self.historyList.hasFocus():
            del self.browserHistory.history[self.historyList.row(self.historyList.currentItem())]
            self.browserHistory.save()
            for tab in range(self.tabs.count()):
                self.tabs.widget(tab).browserHistory.history = self.browserHistory.history
                self.tabs.widget(tab).browserHistory.save()
            self.reloadHistory()
    def showClearHistoryDialog(self):
        self.clearHistoryToolBar.setVisible(not self.clearHistoryToolBar.isVisible())
    def clearHistoryRange(self, timeRange=0.0):
        saveTime = time.time()
        for item in self.browserHistory.history:
            difference = saveTime - item[3]
            if difference <= timeRange:
                del self.browserHistory.history[self.browserHistory.history.index(item)]
        self.browserHistory.save()
        for tab in range(self.tabs.count()):
            self.tabs.widget(tab).browserHistory.history = self.browserHistory.history
            self.tabs.widget(tab).browserHistory.save()
        self.reloadHistory()
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
            saveMonth = time.strftime("%B")
            saveDay = time.strftime("%d")
            now = datetime.datetime.now()
            saveYear = "%d" % now.year
            for item in self.browserHistory.history:
                if item[6] == saveMonth and item[7] == saveDay and item[8] == saveYear:
                    del self.browserHistory.history[self.browserHistory.history.index(item)]
            self.browserHistory.save()
            for tab in range(self.tabs.count()):
                self.tabs.widget(tab).browserHistory.history = self.browserHistory.history
                self.tabs.widget(tab).browserHistory.save()
            self.reloadHistory()
        elif self.selectRange.currentIndex() == 12:
            self.browserHistory.history = []
            self.browserHistory.save()
            for tab in range(self.tabs.count()):
                self.tabs.widget(tab).browserHistory.history = self.browserHistory.history
                self.tabs.widget(tab).browserHistory.save()
            self.reloadHistory()
        elif self.selectRange.currentIndex() == 14:
            self.killCookies = True
            message("Cookies will be cleared on browser restart.", "Ryouko says...", "warn")
    def historyToggle(self):
        self.historyDock.setVisible(not self.historyDock.isVisible())
        if self.historyDock.isVisible():
            self.focusHistorySearch()
    def focusHistorySearch(self):
        self.searchHistoryField.setFocus()
        self.searchHistoryField.selectAll()
    def closeTab(self, index=False):
        if index == False:
            index = self.tabs.currentIndex()
        if self.tabs.count() > 1:
            self.closedTabList.append(self.tabs.widget(index))
            self.tabs.removeTab(index)
    def undoCloseTab(self, index=False):
        if len(self.closedTabList) > 0:
            self.tabs.addTab(self.closedTabList[len(self.closedTabList) - 1], self.closedTabList[len(self.closedTabList) - 1].webView.icon(), self.closedTabList[len(self.closedTabList) - 1].webView.title())
            del self.closedTabList[len(self.closedTabList) - 1]
            self.updateTitles()
            self.tabs.setCurrentIndex(self.tabs.count() - 1)
    def updateIcons(self):
        for tab in range(self.tabs.count()):
            self.tabs.setTabIcon(tab, self.tabs.widget(tab).webView.icon())

    # This part was borrowed from devicenzo:
    def put(self, key, value):
        "Persist an object somewhere under a given key"
        settings.setValue(key, json.dumps(value))
        settings.sync()

    def get(self, key, default=None):
        "Get the object stored under 'key' in persistent storage, or the default value"
        v = settings.value(key)
        return json.loads(unicode(v.toString())) if v.isValid() else default
    # end

    def updateTitles(self):
        for tab in range(self.tabs.count()):
            if str(self.tabs.widget(tab).webView.title()) == "":
                self.tabs.setTabText(tab, "New Tab")
                if tab == self.tabs.currentIndex():
                    self.setWindowTitle("Ryouko")
            else:
                if len(str(self.tabs.widget(tab).webView.title())) > 20:
                    title = ""
                    chars = 0
                    for char in str(self.tabs.widget(tab).webView.title()):
                        title += char
                        chars += 1
                        if chars >= 19:
                            title = title + "..."
                            break
                    title = qstring(title)
                else:
                    title = self.tabs.widget(tab).webView.title()
                self.tabs.setTabText(tab, title)
                if tab == self.tabs.currentIndex():
                    self.setWindowTitle(self.tabs.widget(tab).webView.title() + " - Ryouko")

def main():
    app = QtGui.QApplication(sys.argv)
    win = TabBrowser()
    if os.path.exists(os.path.join(app_lib, "icons", "logo.svg")):
        win.setWindowIcon(QtGui.QIcon(os.path.join(app_lib, "icons", "logo.svg")))
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
