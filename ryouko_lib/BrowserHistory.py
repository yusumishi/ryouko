#! /usr/bin/env python

from __future__ import print_function
import os, sys, json, time, datetime
from PyQt4 import QtCore
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)
from Python23Compat import *

class BrowserHistory(QtCore.QObject):
    historyChanged = QtCore.pyqtSignal()
    def __init__(self, app_profile, parent=None):
        super(BrowserHistory, self).__init__()
        self.parent = parent
        self.history = []
        self.setAppProfile(app_profile)
        self.url = "about:blank"
        if not os.path.exists(os.path.join(self.app_profile, "history.json")):
            self.save()
        self.reload()
    def setAppProfile(self, profile):
        self.app_profile = profile
        try: self.reload()
        except:
            print("", end="")
    def reload(self):
        if os.path.exists(os.path.join(self.app_profile, "history.json")):
            history = open(os.path.join(self.app_profile, "history.json"), "r")
            try: self.history = json.load(history)
            except:
                global reset
                reset = True
            history.close()
    def save(self):
        if not os.path.isdir(self.app_profile):
            os.makedirs(self.app_profile)
        history = open(os.path.join(self.app_profile, "history.json"), "w")
        json.dump(self.history, history)
        history.close()
        self.historyChanged.emit()
    def append(self, url, name=""):
        if unicode(url.toString()) != "about:blank":
            try:
                self.reload()
                self.url = unicode(url.toString())
                url = unicode(url.toString())
                if url != "about:blank":
                    now = datetime.datetime.now()
                    add = True
                    index = 0
                    count = 1
                    for item in self.history:
                        if item['url'] == url:
                            add = False
                            index = self.history.index(item)
                            break
                    if add == True:
                        self.history.insert(0, {'url' : url, 'name' : name, 'count' : count, 'time' : time.time(), 'weekday' : time.strftime("%A"), 'month' : time.strftime("%m"), 'monthday' : time.strftime("%d"), 'year' : "%d" % now.year, 'timestamp' : time.strftime("%H:%M:%S")})
                    else:
                        if not 'count' in self.history[index]:
                            self.history[index]['count'] = 1
                        if not type(self.history[index]['count']) is int:
                            self.history[index]['count'] = 1
                        count = self.history[index]['count'] + 1
                        self.history[index]['count'] = count
                        self.history[index]['time'] = time.time()
                        self.history[index]['weekday'] = time.strftime("%A")
                        self.history[index]['month'] = time.strftime("%m")
                        self.history[index]['monthday'] = time.strftime("%d")
                        self.history[index]['year'] = "%d" % now.year
                        self.history[index]['timestamp'] = time.strftime("%H:%M:%S")
                        tempIndex = self.history[index]
                        del self.history[index]
                        self.history.insert(0, tempIndex)
                self.save()
                self.historyChanged.emit()
            except:
                self.reset()
    def reset(self):
        self.history = []
        self.save()
        self.reload()
    def updateTitles(self, title):
        try:
            self.reload()
            title = unicode(title)
            for item in self.history:
                if item['url'].lower() == self.url.lower():
                    item['name'] = title
            self.save()
            self.historyChanged.emit()
        except:
            self.reset()
    def removeByName(self, name=""):
        try:
            self.reload()
            for item in self.history:
                if item['name'] == name:
                    del self.history[self.history.index(item)]
            self.save()
            self.historyChanged.emit()
        except:
            pass
    def removeByUrl(self, url=""):
        try:
            self.reload()
            for item in self.history:
                if item['url'] == url:
                    del self.history[self.history.index(item)]
            self.historyChanged.emit()
            self.save()
        except:
            pass
