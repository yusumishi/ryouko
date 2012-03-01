#! /usr/bin/env python

from __future__ import print_function

import os, sys, pickle, json, time, datetime
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
if not sys.platform.startswith("win"):
    from PyQt4 import uic
    class Ui_MainWindow():
        pass
else:
    from mainwindow import Ui_MainWindow
try: from urllib.request import urlretrieve
except ImportError:
    try: from urllib import urlretrieve
    except:
        print("", end="")

try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)
app_home = os.path.expanduser(os.path.join("~", ".ryouko-data"))
app_logo = os.path.join(app_lib, "icons", "logo.svg")

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

def message(title="Alert", content="This is a message.", icon="info"):
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

def inputDialog(title="Query", content="Enter a value here:", value=""):
    text = QtGui.QInputDialog.getText(None, title, content, QtGui.QLineEdit.Normal, value)
    if text[1]:
        if unicode(text[0]) != "":
            return text[0]
        else:
            return ""
    else:
        return ""

class BrowserHistory():
    def __init__(self):
        self.history = []
        self.url = "about:blank"
        self.app_home = app_home
        if not os.path.exists(os.path.join(self.app_home, "history.json")):
            self.save()
        self.reload()
    def reload(self):
        if os.path.exists(os.path.join(self.app_home, "history.json")):
            history = open(os.path.join(self.app_home, "history.json"), "r")
            self.history = json.load(history)
            history.close()
    def save(self):
        history = open(os.path.join(self.app_home, "history.json"), "w")
        json.dump(self.history, history)
        history.close()
    def append(self, url, name=""):
        try:
            self.reload()
            self.url = str(url.toString())
            url = str(url.toString())
            if url != "about:blank":
                now = datetime.datetime.now()
                add = True
                index = 0
                count = 1
                for item in self.history:
                    if item['url'].lower() == url:
                        add = False
                        index = self.history.index(item)
                        break
                if add == True:
                    self.history.insert(0, {'url' : url, 'name' : name, 'count' : count, 'time' : time.time(), 'weekday' : time.strftime("%A"), 'month' : time.strftime("%B"), 'monthday' : time.strftime("%d"), 'year' : "%d" % now.year, 'timestamp' : time.strftime("%H:%M:%S")})
                else:
                    if not 'count' in self.history[index]:
                        self.history[index]['count'][1]
                    if not type(self.history[index]['count']) is int:
                        self.history[index]['count'] = 1
                    count = self.history[index]['count'] + 1
                    self.history[index]['count'] = count
                    self.history[index]['time'] = time.time()
                    tempIndex = self.history[index]
                    del self.history[index]
                    self.history.insert(0, tempIndex)
            self.save()
        except:
            self.reset()
    def reset(self):
        message("Ryouko says...", "Oh, no! An error has occurred while trying to access or modify the history! Ryouko is now going to clear the history in an attempt to fix this. =(", "critical")
        self.history = []
        self.save()
        self.reload()
    def updateTitles(self, title):
        try:
            self.reload()
            title = str(title)
            for item in self.history:
                if item['url'].lower() == self.url.lower():
                    item['name'] = title
            self.save()
        except:
            self.reset()
    def removeByName(self, name=""):
        try:
            self.reload()
            for item in self.history:
                if item['name'].lower() == name.lower():
                    del item
            self.save()
        except:
            self.reset()
    def removeByUrl(self, url=""):
        try:
            self.reload()
            for item in self.history:
                if item['url'].lower() == url.lower():
                    del item
            self.save()
        except:
            self.reset()

browserHistory = BrowserHistory()

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
    def __init__(self, parent=False):
        super(RWebView, self).__init__()
        if os.path.exists(app_logo):
            self.setWindowIcon(QtGui.QIcon(app_logo))
        if parent == False or parent == None:
            self.setWindowTitle("Ryouko (PB)")
        else:
            self.setWindowTitle("Ryouko")
        if unicode(self.url().toString()) == "about:blank" or unicode(self.url().toString()) == "":
            self.showShortcuts()
        if parent == False:
            self.parent = None
        self.app_home = app_home

        self.titleChanged.connect(self.updateTitle)

        self.text = ""

        self.showShortcutsAction = QtGui.QAction(self)
        self.showShortcutsAction.setShortcut("F1")
        self.showShortcutsAction.triggered.connect(self.showShortcuts)
        self.addAction(self.showShortcutsAction)

        self.newWindowAction = QtGui.QAction(self)
        self.newWindowAction.setShortcut("Ctrl+N")
        self.newWindowAction.triggered.connect(self.newWindow)
        self.addAction(self.newWindowAction)
        
        self.backAction = QtGui.QAction(self)
        self.backAction.setShortcut("Alt+Left")
        self.backAction.triggered.connect(self.back)
        self.addAction(self.backAction)

        self.nextAction = QtGui.QAction(self)
        self.nextAction.setShortcut("Alt+Right")
        self.nextAction.triggered.connect(self.forward)
        self.addAction(self.nextAction)

        self.reloadAction = QtGui.QAction(self)
        self.reloadAction.triggered.connect(self.reload)
        self.reloadAction.setShortcuts(["Ctrl+R", "F5"])
        self.addAction(self.reloadAction)

        self.findAction = QtGui.QAction(self)
        self.findAction.triggered.connect(self.find)
        self.findAction.setShortcut("Ctrl+F")
        self.addAction(self.findAction)

        self.findNextAction = QtGui.QAction(self)
        self.findNextAction.triggered.connect(self.findNext)
        self.findNextAction.setShortcuts(["Ctrl+G", "F3"])
        self.addAction(self.findNextAction)

        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.downloadFile)
        self.page().downloadRequested.connect(self.downloadFile)
        self.establishParent(parent)

    def establishParent(self, parent):
        if parent == False:
            self.parent = None
        else:
            self.parent = parent
        if not parent or parent == None:
            self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, True)
        else:
            self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, False)
        if parent and self.parent != None:
            self.page().networkAccessManager().setCookieJar(self.parent.cookies)
        else:
            cookies = QtNetwork.QNetworkCookieJar(None)
            cookies.setAllCookies([])
            self.page().networkAccessManager().setCookieJar(cookies)

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
        if self.parent == None or self.parent == False:
            self.setWindowTitle(qstring(unicode(self.title()) + " (PB)"))
        else:
            self.setWindowTitle(self.title())

    def showShortcuts(self):
        self.load(QtCore.QUrl("about:blank"))
        self.setHtml("<html><head><title>Keyboard shortcuts</title></head><body style='font-family: sans-serif;'><center><h1 style='margin-bottom: 0;'>Keyboard shortcuts</h1><br>F1: Show this list of shortcuts<br>Ctrl+N: New window<br>Ctrl+W: Close window<br>Alt+Left: Go back<br>Alt+Right: Go forward<br>Ctrl+R; F5: Reload<br>Esc: Stop<br>Ctrl+L; Alt+D: Open URL<br>Ctrl+F: Find text<br>Ctrl+G; F3: Find next</body></html>")

    def inputDialog(self, title="Query", content="Enter a value here:", value=""):
        text = QtGui.QInputDialog.getText(None, title, content, QtGui.QLineEdit.Normal, value)
        if text[1]:
            if unicode(text[0]) != "":
                return text[0]
            else:
                return ""
        else:
            return ""

    def locationEdit(self):
        url = self.inputDialog("Open location", "Enter a URL here:", self.url().toString())
        if url:
            header = ""
            if not unicode(url).startswith("about:") and not "://" in unicode(url):
                header = "http://"
            url = qstring(header + unicode(url))
            self.load(QtCore.QUrl(url))

    def find(self):
        find = self.inputDialog("Find", "Search for:", self.text)
        if find:
            self.text = find
            self.findText(self.text)
        else:
            self.text = ""
            self.findText(self.text)

    def findNext(self):
        if not self.text:
            self.find()
        else:
            self.findText(self.text)

    def newWindow(self):
       self.createWindow(QtWebKit.QWebPage.WebBrowserWindow)

    def createWindow(self, windowType):
        if not self.parent == None:
            exec("self.newWindow" + str(len(self.newWindows)) + " = RWebView(self.parent)")
        else:
            exec("self.newWindow" + str(len(self.newWindows)) + " = RWebView(None)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction = QtGui.QAction(self.newWindow" + str(len(self.newWindows)) + ")")
        exec("self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction.setShortcut('Ctrl+W')")
        exec("self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction.triggered.connect(self.newWindow" + str(len(self.newWindows)) + ".close)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".addAction(self.newWindow" + str(len(self.newWindows)) + ".closeWindowAction)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".stopAction = QtGui.QAction(self.newWindow" + str(len(self.newWindows)) + ")")
        exec("self.newWindow" + str(len(self.newWindows)) + ".stopAction.setShortcut('Esc')")
        exec("self.newWindow" + str(len(self.newWindows)) + ".stopAction.triggered.connect(self.newWindow" + str(len(self.newWindows)) + ".stop)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".addAction(self.newWindow" + str(len(self.newWindows)) + ".stopAction)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".locationEditAction = QtGui.QAction(self.newWindow" + str(len(self.newWindows)) + ")")
        exec("self.newWindow" + str(len(self.newWindows)) + ".locationEditAction.setShortcuts(['Ctrl+L', 'Alt+D'])")
        exec("self.newWindow" + str(len(self.newWindows)) + ".locationEditAction.triggered.connect(self.newWindow" + str(len(self.newWindows)) + ".locationEdit)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".addAction(self.newWindow" + str(len(self.newWindows)) + ".locationEditAction)")
        exec("self.newWindow" + str(len(self.newWindows)) + ".show()")
        if not self.parent == None:
            exec("self.newWindows.append(self.newWindow" + str(len(self.newWindows)) + ")")
        else:
            exec("self.newWindows.append(None)")
        self.createNewWindow.emit(windowType)
        return self.newWindows[len(self.newWindows) - 1]

class HistoryCompletionList(QtGui.QListWidget):
    statusMessage = QtCore.pyqtSignal(QtCore.QString)
    def __init__(self, parent=None):
        super(HistoryCompletionList, self).__init__()
        self.parent = parent
        self.setMouseTracking(True)
    def mouseMoveEvent(self, ev):
        try: self.statusMessage.emit(qstring(self.parent.tempHistory[self.row(self.itemAt(QtGui.QCursor().pos().x() - self.mapToGlobal(QtCore.QPoint(0,0)).x(), QtGui.QCursor().pos().y() - self.mapToGlobal(QtCore.QPoint(0,0)).y()))]['url']))
        except:
            try: self.statusMessage.emit(qstring(self.parent.tempHistory[self.row(self.itemAt(QtGui.QCursor().pos().x() - self.mapToGlobal(QtCore.QPoint(0,0)).x(), QtGui.QCursor().pos().y() - self.mapToGlobal(QtCore.QPoint(0,0)).y()))]['url']))
            except:
                self.statusMessage.emit(qstring(""))

class Browser(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, url="about:blank", pb=False):
        super(Browser, self).__init__()
        self.parent = parent
        self.pb = pb
        self.app_home = app_home
        self.tempHistory = []
        if not os.path.exists(self.app_home):
            os.mkdir(self.app_home)
        if not self.pb:
            browserHistory = BrowserHistory()
        self.app_lib = app_lib
        self.findText = ""
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
        if not sys.platform.startswith("win"):
            uic.loadUi(os.path.join(self.app_lib, "mainwindow.ui"), self)
        else:
            self.setupUi(self)
        self.webView = RWebView(None)
        self.updateSettings()
        self.webView.statusBarMessage.connect(self.statusMessage.setText)
        self.mainLayout.addWidget(self.webView, 2, 0)
        self.historyCompletion = HistoryCompletionList(self)
        self.historyCompletion.itemActivated.connect(self.openHistoryItem)
        self.historyCompletion.statusMessage.connect(self.statusMessage.setText)
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
        self.backButton.setIcon(QtGui.QIcon().fromTheme("go-previous", QtGui.QIcon(os.path.join(app_lib, "icons", 'back.png'))))
        self.backButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.nextButton.clicked.connect(self.webView.forward)
        self.nextButton.setText("")
        self.nextButton.setIcon(QtGui.QIcon().fromTheme("go-next", QtGui.QIcon(os.path.join(app_lib, "icons", 'next.png'))))
        self.nextButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.urlBar.returnPressed.connect(self.updateWeb)
        if not self.pb:
            self.urlBar.textChanged.connect(self.searchHistory)
        self.webView.urlChanged.connect(self.updateText)
        if not self.pb:
            self.webView.urlChanged.connect(browserHistory.append)
            self.webView.titleChanged.connect(browserHistory.updateTitles)
        self.searchButton.clicked.connect(self.searchWeb)
        self.searchButton.setShortcut("Ctrl+K")
        self.searchButton.setFocusPolicy(QtCore.Qt.NoFocus)
        historySearchAction = QtGui.QAction(self)
        historySearchAction.triggered.connect(self.parent.focusHistorySearch)
        historySearchAction.setShortcuts(["Ctrl+Shift+K", "Ctrl+Shift+H"])
        self.addAction(historySearchAction)
        self.reloadButton.clicked.connect(self.webView.reload)
        self.reloadButton.setText("")
        self.reloadButton.setIcon(QtGui.QIcon().fromTheme("view-refresh", QtGui.QIcon(os.path.join(app_lib, "icons", 'reload.png'))))
        self.reloadButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.findButton.clicked.connect(self.webView.find)
        self.findButton.setText("")
        self.findButton.setIcon(QtGui.QIcon().fromTheme("edit-find", QtGui.QIcon(os.path.join(app_lib, "icons", 'find.png'))))
        self.findButton.setFocusPolicy(QtCore.Qt.NoFocus)

        self.stopAction = QtGui.QAction(self)
        self.stopAction.triggered.connect(self.webView.stop)
        self.stopAction.triggered.connect(self.historyCompletion.hide)
        self.stopAction.triggered.connect(self.updateText)
        self.stopAction.setShortcut("Esc")
        self.addAction(self.stopAction)
        self.stopButton.clicked.connect(self.webView.stop)
        self.stopButton.clicked.connect(self.historyCompletion.hide)
        self.stopButton.clicked.connect(self.updateText)
        self.stopButton.setText("")
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
        self.webView.settings().setIconDatabasePath(qstring(self.app_home))
        self.webView.page().linkHovered.connect(self.updateStatusMessage)
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

    def updateStatusMessage(self, link="", title="", content=""):
        self.statusMessage.setText(qstring(link))

    def updateSettings(self):
        settingsFile = os.path.join(app_home, "settings.json")
        if os.path.exists(settingsFile):
            fstream = open(settingsFile, "r")
            settings = json.load(fstream)
            fstream.close()
        else:
            settings = {'loadImages' : True, 'jsEnabled' : True, 'pluginsEnabled' : False, 'privateBrowsing' : False}
        try: settings['loadImages']
        except: 
            print("", end = "")
        else:
            self.webView.settings().setAttribute(QtWebKit.QWebSettings.AutoLoadImages, settings['loadImages'])
        try: settings['jsEnabled']
        except: 
            print("", end = "")
        else:
            self.webView.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, settings['jsEnabled'])
        try: self.settings['pluginsEnabled']
        except: 
            print("", end = "")
        else:
            self.webView.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, settings['pluginsEnabled'])
        try: settings['privateBrowsing']
        except: 
            print("", end = "")
        else:
            self.webView.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, settings['privateBrowsing'])
            if not settings['privateBrowsing'] and self.pb == False:
                self.webView.establishParent(self.parent)

    def searchHistory(self, string):
        string = unicode(string)
        if string != "" and string != str(self.webView.url().toString()) and string != "about:version":
            self.searchOn = True
            self.historyCompletion.clear()
            history = []
            string = unicode(string)
            for item in browserHistory.history:
                add = False
                for subitem in item:
                    if string.lower() in unicode(item[subitem]).lower():
                        add = True
                if add == True:
                    history.append(item)
                    self.historyCompletion.addItem(item['name'])
            self.tempHistory = history
            self.historyCompletion.show()
            self.webView.hide()
        else:
            self.historyCompletion.hide()
            self.webView.show()
    def openHistoryItem(self, item):
        self.webView.load(QtCore.QUrl(self.tempHistory[self.historyCompletion.row(item)]['url']))
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
        if not unicode(urlBar).startswith("about:") and not "://" in unicode(urlBar):
            header = "http://"
        url = qstring(header + unicode(urlBar))
        if unicode(urlBar) == "about:" or unicode(urlBar) == "about:version":
            self.webView.setHtml("<html><head><title>About Ryouko</title></head><body style='font-family: sans-serif;'><center><h1 style='margin-bottom: 0;'>About Ryouko</h1><img src='file://" + os.path.join(app_lib, "icons", "about-logo.png") + "'></img><br><b>Ryouko version:</b> "+self.version+"<br><b>Release series:</b> \""+self.codename+"\"<br><b>Python version:</b> "+str(sys.version_info[0])+"."+str(sys.version_info[1])+"."+str(sys.version_info[2])+"<br><b>Qt version:</b> "+QtCore.qVersion()+"<br></center></body></html>")
        else:
            url = QtCore.QUrl(url)
            self.webView.load(url)
    def updateText(self):
        url = self.webView.url()
        texturl = url.toString()
        self.urlBar.setText(texturl)

class CDialog(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(CDialog, self).__init__()
        self.parent = parent
        self.settings = {'loadImages' : True, 'jsEnabled' : True, 'pluginsEnabled' : False, 'privateBrowsing' : False}
        self.initUI()
    def initUI(self):
        self.setWindowTitle("Preferences")
        self.setWindowIcon(QtGui.QIcon(app_logo))
        self.mainWidget = QtGui.QWidget()
        self.setCentralWidget(self.mainWidget)
        self.layout = QtGui.QVBoxLayout()
        self.mainWidget.setLayout(self.layout)
        self.imagesBox = QtGui.QCheckBox("Automatically load &images")
        self.layout.addWidget(self.imagesBox)
        self.jsBox = QtGui.QCheckBox("Enable &Javascript")
        self.layout.addWidget(self.jsBox)
        self.pluginsBox = QtGui.QCheckBox("Enable &plugins")
        self.layout.addWidget(self.pluginsBox)
        self.pbBox = QtGui.QCheckBox("Enable private &browsing mode")
        self.layout.addWidget(self.pbBox)
        self.cToolBar = QtGui.QToolBar()
        self.cToolBar.setStyleSheet("""
        QToolBar {
        border: 0;
        background: transparent;
        }

        QToolButton, QPushButton {
        padding: 4px;
        margin-left: 2px;
        border-radius: 4px;
        border: 1px solid palette(shadow);
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(light), stop:1 palette(button));
        }

        QToolButton:pressed, QPushButton:pressed {
        border: 1px solid palette(shadow);
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,     stop:0 palette(shadow), stop:1 palette(button));
        }
        """)
        self.cToolBar.setMovable(False)
        self.cToolBar.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        applyAction = QtGui.QAction("&Apply", self)
        applyAction.setShortcut("Ctrl+S")
        applyAction.triggered.connect(self.saveSettings)
        closeAction = QtGui.QAction("&Close", self)
        closeAction.setShortcut("Esc")
        closeAction.triggered.connect(self.hide)
        self.cToolBar.addAction(applyAction)
        self.cToolBar.addAction(closeAction)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.cToolBar)
        self.loadSettings()
    def loadSettings(self):
        settingsFile = os.path.join(app_home, "settings.json")
        if os.path.exists(settingsFile):
            fstream = open(settingsFile, "r")
            self.settings = json.load(fstream)
            fstream.close()
        try: self.settings['loadImages']
        except: 
            print("", end = "")
        else:
            self.imagesBox.setChecked(self.settings['loadImages'])
        try: self.settings['jsEnabled']
        except: 
            print("", end = "")
        else:
            self.jsBox.setChecked(self.settings['jsEnabled'])
        try: self.settings['pluginsEnabled']
        except: 
            print("", end = "")
        else:
            self.pluginsBox.setChecked(self.settings['pluginsEnabled'])
        try: self.settings['privateBrowsing']
        except: 
            print("", end = "")
        else:
            self.pbBox.setChecked(self.settings['privateBrowsing'])
        self.parent.updateSettings()
    def saveSettings(self):
        settingsFile = os.path.join(app_home, "settings.json")
        self.settings = {'loadImages' : self.imagesBox.isChecked(), 'jsEnabled' : self.jsBox.isChecked(), 'pluginsEnabled' : self.pluginsBox.isChecked(), 'privateBrowsing' : self.pbBox.isChecked()}
        fstream = open(settingsFile, "w")
        json.dump(self.settings, fstream)
        fstream.close()
        self.parent.updateSettings()

class TabBrowser(QtGui.QMainWindow):
    def __init__(self, parent=None):
        super(TabBrowser, self).__init__()
        self.parent = parent
        if sys.version_info[0] >= 3:
            self.cookieFile = os.path.join(app_home, "cookies.pkl")
        else:
            self.cookieFile = os.path.join(app_home, "cookies-py2.pkl")
        self.tabCount = 0
        self.killCookies = False
        self.closedTabList = []
        self.app_home = app_home
        if not os.path.exists(self.app_home):
            os.mkdir(self.app_home)
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
            if sys.platform.startswith("linux"):
                os.system("shred -v \"" + self.cookieFile + "\"")
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

        # History sidebar
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

        # Tabs
        self.tabs = QtGui.QTabWidget()
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

        # "Toolbar" for top right corner
        self.cornerWidgets = QtGui.QWidget()
        self.cornerWidgets.setStyleSheet("""
        QToolButton, QPushButton {
        min-width: 24px;
        border: 1px solid transparent;
        padding: 4px;
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
        self.tabs.setCornerWidget(self.cornerWidgets,QtCore.Qt.TopRightCorner)
        self.cornerWidgetsLayout = QtGui.QHBoxLayout()
        self.cornerWidgetsLayout.setContentsMargins(0,0,0,0)
        self.cornerWidgetsLayout.setSpacing(0)
        self.cornerWidgets.setLayout(self.cornerWidgetsLayout)

        # New tab button
        newTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("tab-new", QtGui.QIcon(os.path.join(os.path.dirname( os.path.realpath(__file__) ), 'newtab.png'))), '&New Tab', self)
        newTabAction.setToolTip("<b>New Tab</b><br>Ctrl+T")
        newTabAction.setShortcuts(['Ctrl+T'])
        newTabAction.triggered.connect(self.newTab)
        self.addAction(newTabAction)
        self.newTabButton = QtGui.QToolButton()
        self.newTabButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.newTabButton.setDefaultAction(newTabAction)
        self.cornerWidgetsLayout.addWidget(self.newTabButton)

        # New window button
        self.newWindowButton = QtGui.QPushButton(QtGui.QIcon().fromTheme("window-new", QtGui.QIcon(os.path.join(os.path.dirname( os.path.realpath(__file__) ), 'newwindow.png'))), '', self)
        self.newWindowButton.setToolTip("<b>New Window</b><br>Ctrl+N")
        self.newWindowButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.newWindowButton.clicked.connect(self.newWindow)
        self.cornerWidgetsLayout.addWidget(self.newWindowButton)

        # Undo closed tab button
        undoCloseTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("edit-undo", QtGui.QIcon(os.path.join(os.path.dirname( os.path.realpath(__file__) ), 'undo.png'))), '&Undo Close Tab', self)
        undoCloseTabAction.setToolTip("<b>Undo Close Tab</b><br>Ctrl+Shift+T")
        undoCloseTabAction.setShortcuts(['Ctrl+Shift+T'])
        undoCloseTabAction.triggered.connect(self.undoCloseTab)
        self.addAction(undoCloseTabAction)
        self.undoCloseTabButton = QtGui.QToolButton()
        self.undoCloseTabButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.undoCloseTabButton.setDefaultAction(undoCloseTabAction)
        self.cornerWidgetsLayout.addWidget(self.undoCloseTabButton)

        # History sidebar button
        historyToggleAction = QtGui.QAction(QtGui.QIcon.fromTheme("document-open-recent", QtGui.QIcon(os.path.join(self.app_lib, "icons", "history.png"))), "Toggle History Sidebar", self)
        historyToggleAction.setToolTip("<b>View History</b><br>Ctrl+H")
        historyToggleAction.triggered.connect(self.historyToggle)
        historyToggleAction.triggered.connect(self.historyToolBar.show)
        historyToggleAction.setShortcut("Ctrl+H")
        self.addAction(historyToggleAction)
        self.historyToggleButton = QtGui.QToolButton()
        self.historyToggleButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.historyToggleButton.setDefaultAction(historyToggleAction)
        self.cornerWidgetsLayout.addWidget(self.historyToggleButton)

        # New private browsing tab button
        newpbTabAction = QtGui.QAction(QtGui.QIcon().fromTheme("face-devilish", QtGui.QIcon(os.path.join(os.path.dirname( os.path.realpath(__file__) ), 'pb.png'))), '&New Private Browsing Tab', self)
        newpbTabAction.setToolTip("<b>New Private Browsing Tab</b><br>Ctrl+Shift+N")
        newpbTabAction.setShortcuts(['Ctrl+Shift+N'])
        newpbTabAction.triggered.connect(self.newpbTab)
        self.addAction(newpbTabAction)
        self.newpbTabButton = QtGui.QToolButton()
        self.newpbTabButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.newpbTabButton.setDefaultAction(newpbTabAction)
        self.cornerWidgetsLayout.addWidget(self.newpbTabButton)

        self.cDialog = CDialog(self)

        # Config button
        configAction = QtGui.QAction(QtGui.QIcon().fromTheme("preferences-system", QtGui.QIcon(os.path.join(os.path.dirname( os.path.realpath(__file__) ), 'settings.png'))), '&Preferences', self)
        configAction.setToolTip("<b>Preferences</b><br>Ctrl+Shift+P")
        configAction.setShortcuts(['Ctrl+Shift+P'])
        configAction.triggered.connect(self.showSettings)
        self.addAction(configAction)
        self.settingsButton = QtGui.QToolButton()
        self.settingsButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.settingsButton.setDefaultAction(configAction)
        self.cornerWidgetsLayout.addWidget(self.settingsButton)

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

    def showSettings(self):
        self.cDialog.show()
        qr = self.cDialog.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.cDialog.move(qr.topLeft())

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
        if self.cDialog.settings['privateBrowsing']:
            self.newpbTab(url)
        else:
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

    def newpbTab(self, url="about:blank"):
        self.tabCount += 1
        if url != False:
            exec("tab" + str(self.tabCount) + " = Browser(self, '"+str(url)+"', True)")
        else:
            exec("tab" + str(self.tabCount) + " = Browser(self, 'about:blank', True)")
        exec("tab" + str(self.tabCount) + ".webView.titleChanged.connect(self.updateTitles)")
        exec("tab" + str(self.tabCount) + ".webView.urlChanged.connect(self.reloadHistory)")
        exec("tab" + str(self.tabCount) + ".webView.titleChanged.connect(self.reloadHistory)")
        exec("tab" + str(self.tabCount) + ".webView.iconChanged.connect(self.updateIcons)")
        exec("self.tabs.addTab(tab" + str(self.tabCount) + ", tab" + str(self.tabCount) + ".webView.icon(), 'New Tab')")
        self.tabs.setCurrentIndex(self.tabs.count() - 1)

    def newWindow(self):
        self.tabs.widget(self.tabs.currentIndex()).webView.newWindow()

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
                    self.historyList.addItem(qstring(str(item['name'])))
            else:
                browserHistory.reload()
        except:
            browserHistory.reset()
    def searchHistory(self, string=""):
        string = str(string)
        if string != "":
            self.searchOn = True
            self.historyList.clear()
            history = []
            string = str(string)
            for item in browserHistory.history:
                add = False
                for subitem in item:
                    if string.lower() in str(subitem).lower():
                        add = True
                if add == True:
                    history.append(item)
                    self.historyList.addItem(item['name'])
            self.tempHistory = history
        else:
            self.searchOn = False
            self.reloadHistory()
    def deleteHistoryItem(self):
        if self.historyList.hasFocus():
            del browserHistory.history[self.historyList.row(self.historyList.currentItem())]
            browserHistory.save()
            for tab in range(self.tabs.count()):
                self.tabs.widget(tab).browserHistory.history = browserHistory.history
                self.tabs.widget(tab).browserHistory.save()
            self.reloadHistory()
    def showClearHistoryDialog(self):
        self.clearHistoryToolBar.setVisible(not self.clearHistoryToolBar.isVisible())
    def clearHistoryRange(self, timeRange=0.0):
        saveTime = time.time()
        for item in browserHistory.history:
            try:
                difference = saveTime - item['time']
            except:
                browserHistory.reset()
                break
            if difference <= timeRange:
                del browserHistory.history[browserHistory.history.index(item)]
        browserHistory.save()
        for tab in range(self.tabs.count()):
            self.tabs.widget(tab).browserHistory.history = browserHistory.history
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
            for item in browserHistory.history:
                if item['month'] == saveMonth and item['monthday'] == saveDay and item['year'] == saveYear:
                    del browserHistory.history[browserHistory.history.index(item)]
            browserHistory.save()
            for tab in range(self.tabs.count()):
                self.tabs.widget(tab).browserHistory.history = browserHistory.history
                self.tabs.widget(tab).browserHistory.save()
            self.reloadHistory()
        elif self.selectRange.currentIndex() == 12:
            browserHistory.history = []
            browserHistory.save()
            for tab in range(self.tabs.count()):
                self.tabs.widget(tab).browserHistory.history = browserHistory.history
                self.tabs.widget(tab).browserHistory.save()
            self.reloadHistory()
        elif self.selectRange.currentIndex() == 14:
            self.killCookies = True
            message("Ryouko says...", "Cookies will be cleared on browser restart.", "warn")
    def historyToggle(self):
        self.historyDock.setVisible(not self.historyDock.isVisible())
        if self.historyDock.isVisible():
            self.focusHistorySearch()
    def focusHistorySearch(self):
        self.searchHistoryField.setFocus()
        self.searchHistoryField.selectAll()
    def closeTab(self, index=False):
        if not index:
            index = self.tabs.currentIndex()
        if self.tabs.count() > 1:
            if not self.tabs.widget(index).pb:
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

    def updateTitles(self):
        for tab in range(self.tabs.count()):
            if str(self.tabs.widget(tab).webView.title()) == "":
                if not self.tabs.widget(tab).pb:
                    self.tabs.setTabText(tab, "New Tab")
                else:
                    self.tabs.setTabText(tab, "New Tab (PB)")
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
                if self.tabs.widget(tab).pb:
                    title = unicode(title)
                    title = title + " (PB)"
                    title = qstring(title)
                self.tabs.setTabText(tab, title)
                if tab == self.tabs.currentIndex():
                    self.setWindowTitle(self.tabs.widget(tab).webView.title() + " - Ryouko")

def main():
    app = QtGui.QApplication(sys.argv)
    win = TabBrowser()
    if os.path.exists(app_logo):
        win.setWindowIcon(QtGui.QIcon(app_logo))
    win.show()
    app.exec_()

if __name__ == "__main__":
    main()
