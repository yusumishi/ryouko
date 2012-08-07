#! /usr/bin/env python

from __future__ import print_function
import os, sys, string, locale
from PyQt4 import QtCore, QtGui, QtWebKit, QtNetwork
try: __file__
except: __file__ == sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)

from Python23Compat import *
from QStringFunctions import *
from DialogFunctions import *
from ViewSourceDialog import *
from TranslationManager import *
from SystemFunctions import *

app_google_docs_extensions = [".doc", ".pdf", ".ppt", ".pptx", ".docx", ".xls", ".xlsx", ".pages", ".ai", ".psd", ".tiff", ".dxf", ".svg", ".eps", ".ps", ".ttf", ".xps", ".zip", ".rar"]
app_zoho_extensions = [".pdf", ".doc", ".docx", ".ppt", ".pptx", ".pps", ".xls", ".xlsx", ".odt", ".ods", ".odp", ".sxw", ".sxc", ".sxi", ".wpd", ".rtf", ".csv", ".tsv", ".txt", ".html"]
app_locale = locale.getdefaultlocale()[0]
app_info = os.path.join(app_lib, "info.txt")
app_version = "N/A"
if os.path.exists(app_info):
    readVersionFile = open(app_info)
    metadata = readVersionFile.readlines()
    readVersionFile.close()
    if len(metadata) > 0:
        app_version = metadata[0].rstrip("\n")

def doNothing():
    return

def do_nothing():
    return

class RWebPage(QtWebKit.QWebPage):
    def __init__(self, parent=None):
        super(RWebPage, self).__init__()
        self.setParent(parent)
        self.userAgent = False
        global app_default_useragent
        app_default_useragent = unicode(self.userAgentForUrl(QtCore.QUrl("about:blank"))).replace("Safari", "Ryouko/" + app_version + " Safari")
        self.bork = False
        self.replyURL = QtCore.QUrl("about:blank")
        self.networkAccessManager().authenticationRequired.connect(self.provideAuthentication)
        self.networkAccessManager().sslErrors.connect(self.sslError)

    def sslError(self, reply, errors):
        q = QtGui.QMessageBox.warning(None, tr("warning"),
    tr("sslWarning"), QtGui.QMessageBox.Yes | 
    QtGui.QMessageBox.No, QtGui.QMessageBox.No)
        if q == QtGui.QMessageBox.Yes:
            reply.ignoreSslErrors()
        else:
            return

    def provideAuthentication(self, reply, auth):
        if self.bork == False:
            uname = QtGui.QInputDialog.getText(None, tr('query'), tr('username') + ":", QtGui.QLineEdit.Normal)
            if uname[1]:
                auth.setUser(uname[0])
                pword = QtGui.QInputDialog.getText(None, tr('query'), tr('password') + ":", QtGui.QLineEdit.Password)
                if pword[1]:
                    auth.setPassword(pword[0])
            if self.replyURL == reply.url():
                self.bork = True
            else:
                self.replyURL = reply.url()
        else:
            reply.abort()
            self.bork = False
            self.replyURL = QtCore.QUrl("about:blank")

    def userAgentForUrl(self, url):
        if self.userAgent == False:
            return QtWebKit.QWebPage.userAgentForUrl(self, url)
        else:
            if sys.version_info[0] <= 2:
                return QtCore.QString(self.userAgent)
            else:
                return str(self.userAgent)

    def setUserAgent(self, string):
        self.userAgent = string
        
    def createPlugin(self, classid, url, paramNames, paramValues):
        if classid == "ctl":
            v = QtGui.QListWidget(self.view())
            try:
                for tab in self.parent().parent().parent.closedTabsList:
                    v.addItem(tab["title"])
                v.itemActivated.connect(self.parent().parent().parent.undoCloseTabInThisTab)
                v.itemClicked.connect(self.parent().parent().parent.undoCloseTabInThisTab)
            except: do_nothing()
            else:
                return v
        elif classid == "fileview":
            f = QtGui.QListWidget(self.view())
            try:
                u = unicode(url.toString()).replace("file://", "")
                f.addItem(os.path.dirname(u))
                if os.path.isdir(u):
                    l = os.listdir(u)
                    l.sort()
                    for fname in l:
                        f.addItem(os.path.join(u, fname))
                f.itemClicked.connect(self.parent().load)
                f.itemActivated.connect(self.parent().load)
            except: do_nothing()
            else: return f
        elif classid == "aboutQt":
            b = QtGui.QPushButton(self.view())
            b.setText(tr("aboutQt"))
            b.clicked.connect(QtGui.QApplication.aboutQt)
            return b
        elif classid == "QTabWidget":
            t = QtGui.QTabWidget(self.view())
            try:
                u = unicode(url.toString()).replace("file://", "").strip("http://")
                ul = u.split("|")
                for url in ul:
                    w = QtGui.QWebView()
                    w.load(QtCore.QUrl(url))
                    block = ""
                    if len(ul) > 20:
                        block = "..."
                    t.addTab(w, ul[0:20] + block)
            except: do_nothing()
            else: return t
        return

class RAboutPageView(QtWebKit.QWebView):
    def __init__(self, parent=None):
        QtWebKit.QWebView.__init__(self, parent)
        page = RWebPage(self)
        self.setPage(page)
        self.systemOpenView = RSystemOpenView(self)
        self.systemOpenView.hide()
        self.page().setLinkDelegationPolicy(QtWebKit.QWebPage.DelegateAllLinks)
        self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, True)
        self.page().linkClicked.connect(self.openLink)
    def openLink(self, url):
        u = unicode(url.toString())
        system_open(u)
    def createWindow(self, windowType):
        return self.systemOpenView

class RSystemOpenView(QtWebKit.QWebView):
    def __init__(self, parent=None):
        QtWebKit.QWebView.__init__(self, parent)
        self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, True)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, False)
        self.settings().setAttribute(QtWebKit.QWebSettings.AutoLoadImages, False)
        self.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, False)
        self.settings().setAttribute(QtWebKit.QWebSettings.JavaEnabled, False)
        self.page().setForwardUnsupportedContent(True)
        self.page().unsupportedContent.connect(self.openFile)
        self.urlChanged.connect(self.loadSupportedFile)
    def loadSupportedFile(self, url):
        system_open(unicode(self.url().toString()))
        self.back()
    def load(self, url):
        system_open(unicode(url().toString()))
    def openFile(self, reply):
        u = unicode(reply.url().toString())
        system_open(u)

class RWebView(QtWebKit.QWebView):
    createNewWindow = QtCore.pyqtSignal(QtWebKit.QWebPage.WebWindowType)
    saveCookies = QtCore.pyqtSignal()
    newTabRequest = QtCore.pyqtSignal(QtWebKit.QWebView)
    newWindowRequest = QtCore.pyqtSignal(QtWebKit.QWebView)
    undoCloseWindowRequest = QtCore.pyqtSignal()
    downloadStarted = QtCore.pyqtSignal()
    def __init__(self, parent=False, settingsManager=None, pb=False, app_profile=os.path.expanduser("~"), sm=None, user_links="", downloadManager=None):
        QtWebKit.QWebView.__init__(self, parent)
        self.settingsManager = settingsManager
        self.user_links = user_links
        self.searchManager = sm
        self.downloadManager = downloadManager
        self.app_profile = app_profile
        self.setCookieJar(QtNetwork.QNetworkCookieJar(None))
        self.parent2 = parent
        page = RWebPage(self)
        self.setPage(page)
        self.settingsManager = None
        self.loading = False
        self.destinations = []
        self.sourceViews = []
        self.autoSaveInterval = 0
        self.urlChanged.connect(self.autoSave)
        self.printer = None
        self.replies = []
        self.newWindows = [0]
        self.settings().setAttribute(QtWebKit.QWebSettings.DeveloperExtrasEnabled, True)
#        if os.path.exists(app_logo):
#            self.setWindowIcon(QtGui.QIcon(app_logo))
        if pb:
            self.setWindowTitle("Ryouko (PB)")
        else:
            self.setWindowTitle("Ryouko")
        if parent == False:
            self.setParent(None)
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

        self.findPreviousAction = QtGui.QAction(self)
        self.findPreviousAction.triggered.connect(self.findPrevious)
        self.findPreviousAction.setShortcut("Ctrl+Shift+G")
        self.addAction(self.findPreviousAction)

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
        self.undoCloseWindowAction.triggered.connect(self.undoCloseWindowRequest.emit)
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
        self.loadFinished.connect(self.setLoadingFalse)
        self.loadProgress.connect(self.setLoadingTrue)
        if (unicode(self.url().toString()) == "about:blank" or unicode(self.url().toString()) == ""):
            self.buildNewTabPage()
        else:
            self.isWindow = False
        self.loadFinished.connect(self.loadLinks)

    def load(self, url):
        if type(url) == QtGui.QListWidgetItem:
            url = QtCore.QUrl(url.text())
        elif url == QtCore.QUrl(unicode("file:")):
            return
        b = unicode(url.toString()).replace("file://", "")
        if os.path.isdir(b):
            self.load(QtCore.QUrl("about:blank"))
            self.setHtml("<!DOCTYPE html><html><head><style type=\"text/css\">*{margin:0;padding:0;}.rbox{display: none; visibility: collapse; position: fixed; max-width: 0; max-height: 0; top: -1px; left: -1px;}</style><title>" + b + "</title></head><body></body><span id=\"ryouko-toolbar\" class=\"rbox\"><span id=\"ryouko-link-bar-container\" class=\"rbox\"></span></span><object type=\"application/x-qt-plugin\" data=\"file://" + b + "\" classid=\"fileview\" style=\"position: fixed; width: 100%; height: 100%;\"></object></body></html>")
        else:
            QtWebKit.QWebView.load(self, url)

    def setUserLinks(self, user_links):
        self.user_links = user_links
#        print(user_links)

    def setSettingsManager(self, settingsManager):
        self.settingsManager = settingsManager

    def setParent(self, parent=None):
        QtWebKit.QWebView.setParent(self, parent)
        self.parent2 = parent

    def setLoadingTrue(self):
        self.loading = True

    def setLoadingFalse(self):
        self.loading = False

    def isLoading(self):
        return self.loading

    def replaceAV(self):
        av = self.page().mainFrame().findAllElements("audio, video")
        if not os.path.exists(os.path.join(self.app_profile, "win-vlc.conf")) and len(av) > 0:
            q = QtGui.QMessageBox.question(None, tr("ryoukoSays"),
        tr("audioVideoUnsupported"), QtGui.QMessageBox.Yes | 
        QtGui.QMessageBox.No, QtGui.QMessageBox.No)
            if q == QtGui.QMessageBox.Yes:
                wv = self.createWindow(QtWebKit.QWebPage.WebBrowserWindow)
                wv.load(QtCore.QUrl("http://www.videolan.org/vlc/index.html"))
            f = open(os.path.join(self.app_profile, "win-vlc.conf"), "w")
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
            self.saveCookies.emit()
            self.autoSaveInterval = 0

    def closeEvent(self, ev):
        return QtGui.QMainWindow.closeEvent(self, ev)

    def showInspector(self):
        if self.parent2.webInspectorDock:
            self.parent2.webInspectorDock.show()
        if self.parent2.webInspector:
            self.parent2.webInspector.show()

    def enableControls(self):
        self.loadFinished.connect(self.loadControls)

    def loadLinks(self):
        try: self.settingsManager.settings["showBookmarksToolBar"]
        except: a = True
        else: a = self.settingsManager.settings["showBookmarksToolBar"]
        if a:
            if not self.user_links == "":
                if self.page().mainFrame().findFirstElement("#ryouko-toolbar").isNull() == True:
                    self.buildToolBar()
                if self.page().mainFrame().findFirstElement("#ryouko-link-bar").isNull():
                    self.page().mainFrame().findFirstElement("#ryouko-link-bar-container").appendInside("<span id=\"ryouko-link-bar\"></span>")
                    if not self.user_links == "":
                        self.page().mainFrame().findFirstElement("#ryouko-link-bar").appendInside(self.user_links)
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

    def runThroughFilters(self, url):
        remove = False
        invert = False
        for f in self.settingsManager.filters:
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

    def checkForAds(self):
        if self.settingsManager != None:
            if self.settingsManager.settings['adBlock']:
                elements = self.page().mainFrame().findAllElements("iframe, frame, object, embed, .ego_unit").toList()
                for element in elements:
                    for attribute in element.attributeNames():
                        e = unicode(element.attribute(attribute))
                        delete = self.runThroughFilters(e)
                        if delete:
                            element.removeFromDocument()
                            break

    def setCookieJar(self, cj):
        self.cookieJar = cj
        self.page().networkAccessManager().setCookieJar(cj)
        cj.setParent(QtCore.QCoreApplication.instance())

    def establishPBMode(self, pb):
        self.pb = pb
        if not pb or pb == None:
            self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, True)
        else:
            self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, False)
        if not pb:
            try:
                self.setCookieJar(self.cookieJar)
            except:
                doNothing()
        else:
            cookies = QtNetwork.QNetworkCookieJar(None)
            cookies.setAllCookies([])
            self.page().networkAccessManager().setCookieJar(cookies)
        if (unicode(self.url().toString()) == "about:blank" or unicode(self.url().toString()) == "") and self.pb != None and self.pb != False:
            self.buildNewTabPage()

    def disablePersistentStorage(self):
        self.settings().setOfflineStoragePath(qstring(""))
        self.settings().setLocalStoragePath(qstring(""))
        self.settings().setOfflineWebApplicationCachePath(qstring(""))
        self.settings().setIconDatabasePath(qstring(""))

    def updateSettings(self):
        if self.settingsManager != None:
            try: self.settingsManager.settings['loadImages']
            except: 
                print("", end = "")
            else:
                self.settings().setAttribute(QtWebKit.QWebSettings.AutoLoadImages, self.settingsManager.settings['loadImages'])
            try: self.settingsManager.settings['jsEnabled']
            except: 
                print("", end = "")
            else:
                self.settings().setAttribute(QtWebKit.QWebSettings.JavascriptEnabled, self.settingsManager.settings['jsEnabled'])
            try: self.settingsManager.settings['javaEnabled']
            except: 
                print("", end = "")
            else:
                self.settings().setAttribute(QtWebKit.QWebSettings.JavaEnabled, self.settingsManager.settings['javaEnabled'])
            try: self.settingsManager.settings['customUserAgent']
            except:
                doNothing()
            else:
                if self.settingsManager.settings['customUserAgent'].replace(" ", "") != "":
                    self.page().setUserAgent(self.settingsManager.settings['customUserAgent'])
                else:
                    self.page().setUserAgent(app_default_useragent)
            try: self.settingsManager.settings['storageEnabled']
            except:
                self.settings().enablePersistentStorage(qstring(self.app_profile))
            else:
                if self.settingsManager.settings['storageEnabled'] == True:
                    self.settings().enablePersistentStorage(qstring(self.app_profile))
                else:
                    self.settings().setOfflineStoragePath(qstring(""))
                    self.settings().setLocalStoragePath(qstring(""))
                    self.settings().setOfflineWebApplicationCachePath(qstring(""))
                    self.settings().setIconDatabasePath(qstring(self.app_profile))
            try: self.settingsManager.settings['pluginsEnabled']
            except: 
                print("", end = "")
            else:
                self.settings().setAttribute(QtWebKit.QWebSettings.PluginsEnabled, self.settingsManager.settings['pluginsEnabled'])
            try: self.settingsManager.settings['privateBrowsing']
            except: 
                print("", end = "")
            else:
                self.settings().setAttribute(QtWebKit.QWebSettings.PrivateBrowsingEnabled, self.settingsManager.settings['privateBrowsing'])
                if self.settingsManager.settings['privateBrowsing'] == True:
                    self.establishPBMode(True)
            try: self.settingsManager.settings['proxy']
            except:
                doNothing()
            else:
                pr = self.settingsManager.settings['proxy']
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
            for child in range(1, len(self.newWindows)):
                try: self.newWindows[child].updateSettings()
                except:
                    print("Error! %s does not have an updateSettings() method!" % (self.newWindows[child]))

    def downloadUnsupportedContent(self, reply):
        url = unicode(reply.url().toString())
        try: self.settingsManager.settings['googleDocsViewerEnabled']
        except:
            d = True
        else:
            d = self.settingsManager.settings['googleDocsViewerEnabled']
        try: self.settingsManager.settings['zohoViewerEnabled']
        except:
            z = True
        else:
            z = self.settingsManager.settings['zohoViewerEnabled']
        if d == True and not "file://" in url:
            for ext in app_google_docs_extensions:
                if url.split("?")[0].lower().endswith(ext):
                    self.stop()
                    self.load(QtCore.QUrl("https://docs.google.com/viewer?embedded=true&url=" + url))
                    return
        if z == True and not "file://" in url:
            for ext in app_zoho_extensions:
                if url.split("?")[0].lower().endswith(ext):
                    self.stop()
                    self.load(QtCore.QUrl("https://viewer.zoho.com/docs/urlview.do?url=" + url))
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
            nm = self.downloadManager.networkAccessManager
            if type(request) == QtNetwork.QNetworkReply:
                reply = nm.get(request.request())
            else:
                reply = nm.get(request)
            self.downloadManager.newReply(reply, fname)
            self.downloadStarted.emit()
            global downloadStartTimer

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
        f = str(self.searchManager.currentSearch.replace("%s", ""))
#        if type(self.parent2) == Browser:
        t = tr('newTab')
#        else:
#            t = tr('newWindow')
        html = "<!DOCTYPE html><html><head><title>" + t + "</title><style type='text/css'>h1{margin-top: 0; margin-bottom: 0;}</style></head><body style='font-family: sans-serif;'><b style='display: inline-block;'>" + tr('search') + ":</b><form method='get' action='" + f + "' style='display: inline-block;'><input type='text'  name='q' size='31' maxlength='255' value='' /><input type='submit' value='" + tr('go') + "' /></form><table style='border: 0; margin: 0; padding: 0; width: 100%;' cellpadding='0' cellspacing='0'><tr valign='top'>"
        h = tr('newTabShortcuts')
        try: self.parent2.parent.closedTabsList
        except:
            doNothing()
        else:
            if len(self.parent2.parent.closedTabsList) > 0:
                html = html + "<td style='border-right: 1px solid; padding-right: 4px;' width=\"49%\"><b>" + tr('rCTabs') + "</b><br/>"
                html = html + "<object type=\"application/x-qt-plugin\" classid=\"ctl\" style=\"width: 100%; height: 85%;\"></object>"
            if not len(self.parent2.parent.closedTabsList) > 0:
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

    def findPrevious(self):
        if not self.text:
            self.find()
        else:
            self.findText(self.text, QtWebKit.QWebPage.FindWrapsAroundDocument | QtWebKit.QWebPage.FindBackward)

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
        if self.settingsManager.settings['openInTabs']:
            webView = RWebView(self, self.settingsManager, self.pb, self.app_profile, self.searchManager, self.user_links, self.downloadManager)
            self.createNewWindow.emit(windowType)
            self.newTabRequest.emit(webView)
            return webView
        else:
            webView = RWebView(self, self.settingsManager,self.pb, self.app_profile, self.searchManager, self.user_links, self.downloadManager)
            self.createNewWindow.emit(windowType)
            self.newWindowRequest.emit(webView)
            return webView
