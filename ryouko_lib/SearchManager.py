#! /usr/bin/env python

import os.path, sys, json
from PyQt4 import QtCore
try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))
sys.path.append(app_lib)
from TranslationManager import *
from Python23Compat import *
from DialogFunctions import message

class SearchManager(QtCore.QObject):
    def __init__(self, app_profile=os.path.expanduser("~"), parent=None):
        super(SearchManager, self).__init__(parent)
        self.parent = parent
        self.searchEngines = {"DuckDuckGo": {"expression" : "http://duckduckgo.com/?q=%s", "keyword" : "d"}, "Wikipedia": {"expression" : "http://wikipedia.org/w/index.php?title=Special:Search&search=%s", "keyword" : "w"}, "YouTube" : {"expression" : "http://www.youtube.com/results?search_query=%s", "keyword" : "y"}, "Google" : {"expression" : "http://www.google.com/?q=%s", "keyword" : "g"}, "deviantART" : {"expression" : "http://browse.deviantart.com/?qh=&section=&q=%s", "keyword" : "da"}}
        self.currentSearch = "http://duckduckgo.com/?q=%s"
        self.app_profile = app_profile
        self.searchEnginesFile = os.path.join(self.app_profile, "search-engines.json")
        self.load()
    def changeProfile(self, profile):
        self.app_profile = profile
        self.searchEnginesFile = os.path.join(self.app_profile, "search-engines.json")
        self.load()
    def load(self):
        if os.path.exists(self.searchEnginesFile):
            f = open(self.searchEnginesFile, "r")
            try: read = json.load(f)
            except:
                pass
            f.close()
            try: read['searchEngines']
            except:
                pass
            else:
                self.searchEngines = read['searchEngines'] 
            try: read['currentSearch']
            except:
                pass
            else:
                self.currentSearch = read['currentSearch']
    def save(self):
        f = open(self.searchEnginesFile, "w")
        json.dump({"searchEngines" : self.searchEngines, "currentSearch" : self.currentSearch}, f)
        f.close()
    def add(self, name=False, expression=False, keyword=""):
        if name and expression:
            self.searchEngines[unicode(name)] = {"expression" : unicode(expression), "keyword" : unicode(keyword)}
            self.save()
    def notificationMessage(self, message):
        message(tr('error'), message, "warn")
    def remove(self, name=False):
        if name:
            try: self.searchEngines[unicode(name)]
            except:
                notificationMessage(tr('searchError'))
            else:
                del self.searchEngines[unicode(name)]
                self.save()
    def change(self, name=""):
        try: self.searchEngines[unicode(name)]["expression"]
        except:
            notificationMessage(tr('searchError'))
        else:
            self.currentSearch = self.searchEngines[unicode(name)]["expression"]
            self.save()
