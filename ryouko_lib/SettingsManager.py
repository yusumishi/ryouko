#! /usr/bin/env python

import os, json
from subprocess import Popen, PIPE

class SettingsManager():
    def __init__(self, app_profile = os.path.join(os.path.expanduser("~"), ".ryouko-data", "profiles", "default")):
        self.settings = {'openInTabs' : True, 'oldSchoolWindows' : False, 'loadImages' : True, 'jsEnabled' : True, 'storageEnabled' : True, 'pluginsEnabled' : False, 'privateBrowsing' : False, 'backend' : 'qt', 'loginToDownload' : False, 'adBlock' : False, 'proxy' : {"type" : "No", "hostname" : "", "port" : "8080", "user" : "", "password" : ""}, "cloudService" : "None", "maxUndoCloseTab" : 0}
        self.filters = []
        self.app_profile = app_profile
        self.loadSettings()
    def changeProfile(self, profile):
        self.app_profile = profile
        self.loadSettings()
    def loadSettings(self):
        settingsFile = os.path.join(self.app_profile, "settings.json")
        if os.path.exists(settingsFile):
            fstream = open(settingsFile, "r")
            self.settings = json.load(fstream)
            fstream.close()
        self.applyFilters()
    def saveSettings(self):
        settingsFile = os.path.join(self.app_profile, "settings.json")
        fstream = open(settingsFile, "w")
        json.dump(self.settings, fstream)
        fstream.close()
    def applyFilters(self):
        if os.path.isdir(os.path.join(self.app_profile, "adblock")):
            self.filters = []
            l = os.listdir(os.path.join(self.app_profile, "adblock"))
            for fname in l:
                f = open(os.path.join(self.app_profile, "adblock", fname))
                contents = f.readlines()
                f.close()
                for g in contents:
                    self.filters.append(g.rstrip("\n"))
    def setBackend(self, backend = "python"):
        check = False
        if backend == "aria2":
            check = Popen(["which", "aria2c"], stdout=PIPE).communicate()[0]
        elif backend != "python" and backend != "qt":
            check = Popen(["which", backend], stdout=PIPE).communicate()[0]
        else:
            check = True
        if check:
            self.settings['backend'] = backend
        else:
            self.errorMessage(backend)
            self.settings['backend'] = "qt"
    def errorMessage(self, backend=""):
        print("Error! Backend %s could not be found!" % (backend))
