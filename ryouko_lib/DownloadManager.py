#! /usr/bin/env/ python

from __future__ import division
import os.path, sys
from PyQt4 import QtCore, QtGui
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
app_icons = os.path.join(app_lib, "icons")
sys.path.append(app_lib)
from Python23Compat import *
from TranslationManager import *

class DownloadProgressBar(QtGui.QProgressBar):
    def __init__(self, reply=None, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressBar, self).__init__()
        self.reply = reply
        self.destination = destination
        self.progress = [0, 0]
        if self.reply:
            self.reply.downloadProgress.connect(self.updateProgress)
            self.reply.finished.connect(self.finishDownload)
    def finishDownload(self):
        if self.reply.isFinished():
            data = self.reply.readAll()
            f = QtCore.QFile(self.destination)
            f.open(QtCore.QIODevice.WriteOnly)
            f.writeData(data)
            f.flush()
            f.close()
            self.progress = [0, 0]
    def updateProgress(self, received, total):
        self.setMaximum(total)
        self.setValue(received)
        self.progress[0] = received
        self.progress[1] = total
        self.show()

class DownloadProgressWidget(QtGui.QWidget):
    def __init__(self, reply=None, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressWidget, self).__init__()
        self.layout = QtGui.QHBoxLayout()
        self.layout.setContentsMargins(0,0,0,0)
        self.setLayout(self.layout)
        self.progressBar = DownloadProgressBar(reply, destination, self)
        self.progressBar.reply.downloadProgress.connect(self.updateProgress)
        self.layout.addWidget(self.progressBar)
        self.reply = self.progressBar.reply
        self.stopButton = QtGui.QToolButton()
        self.stopButton.setIcon(QtGui.QIcon().fromTheme("process-stop", QtGui.QIcon(os.path.join(app_icons, 'stop.png'))))
        self.stopButton.clicked.connect(self.abort)
        self.layout.addWidget(self.stopButton)
        self.yay = True
        self.progress = [0, 0]
    def updateProgress(self, received, total):
        self.progress[0] = received
        self.progress[1] = total
    def abort(self):
        self.yay = False
        self.progressBar.reply.abort()
        self.progressBar.reply.finished.emit()

class DownloadProgressDialog(QtGui.QProgressBar):
    def __init__(self, reply=None, destination=os.path.expanduser("~"), parent=None):
        super(DownloadProgressDialog, self).__init__()
        self.reply = reply
        self.destination = destination
        self.progress = [0, 0]
        if self.reply:
            self.reply.downloadProgress.connect(self.updateProgress)
            self.reply.finished.connect(self.finishDownload)
        self.setWindowTitle(os.path.split(unicode(destination))[1])
    def finishDownload(self):
        if self.reply.isFinished():
            data = self.reply.readAll()
            f = QtCore.QFile(self.destination)
            f.open(QtCore.QIODevice.WriteOnly)
            f.writeData(data)
            f.flush()
            f.close()
            self.progress = [0, 0]
            self.hide()
    def updateProgress(self, received, total):
        self.setMaximum(total)
        self.setValue(received)
        self.progress[0] = received
        self.progress[1] = total
        self.show()

class DownloadManagerGUI(QtGui.QMainWindow):
    downloadProgress = QtCore.pyqtSignal(float)
    downloadFinished = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        super(DownloadManagerGUI, self).__init__()
        self.downloads = []

        self.setWindowTitle(tr('downloads'))

        closeWindowAction = QtGui.QAction(self)
        closeWindowAction.setShortcuts(["Ctrl+W", "Esc", "Ctrl+Shift+Y", "Ctrl+J"])
        closeWindowAction.triggered.connect(self.hide)
        self.addAction(closeWindowAction)

        self.scrollArea = QtGui.QScrollArea()
        self.scrollArea.setMinimumHeight(256)
        self.scrollArea.setMinimumWidth(400)
        self.scrollArea.setWidgetResizable(True)
        self.setCentralWidget(self.scrollArea)

        self.centralWidget = QtGui.QWidget()
        self.scrollArea.setWidget(self.centralWidget)

        self.layout = QtGui.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignTop)
        self.layout.setContentsMargins(0,0,0,0)
        self.centralWidget.setLayout(self.layout)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.checkProgress)
        self.timer.start(1250)

    def newReply(self, reply, destination = os.path.expanduser("~")):
        i = DownloadProgressWidget(reply, destination)
        self.downloads.append(i)
        reply.finished.connect(self.checkForFinishedDownloads)
        self.layout.addWidget(i)
        self.show()
        self.activateWindow()

    def checkProgress(self):
        pr = 0.0
        pt = 0.0
        for p in self.downloads:
            pr = pr + float(p.progress[0])
            pt = pt + float(p.progress[1])
        if pt != 0.0:
            pe = pr/pt
        else:
            pe = 0.0
        if pe == 0.0:
            self.setWindowTitle(tr('downloads'))
        else:
            self.setWindowTitle(tr('downloads') + " - " + str(int(pe*100)) + "%")
        self.downloadProgress.emit(pe)
            
    def checkForFinishedDownloads(self):
        for i in range(len(self.downloads)):
            if self.downloads[i].reply.isFinished():
                if self.downloads[i].yay == False:
                    aborted = True
                else:
                    aborted = False
                self.downloads[i].deleteLater()
                del self.downloads[i]
                if aborted == False:
                    self.downloadFinished.emit()
                break
