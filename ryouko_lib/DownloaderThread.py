#! /usr/bin/env python

from __future__ import print_function
import os, sys
try: from urllib.request import urlretrieve
except ImportError:
    try: from urllib import urlretrieve
    except:
        print("", end="")
    else:
        import urllib
else:
    import urllib.request
from PyQt4 import QtCore
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)
from Python23Compat import *
from SystemTerminal import *

def urlretrieve_adv(url, filename=None, reporthook=None, data=None, username="", password=""):
    if sys.version_info[0] < 3:
        class OpenerWithAuth(urllib.FancyURLopener):
            def prompt_user_passwd(self, host, realm):
                return username, password
    else:
        class OpenerWithAuth(urllib.request.FancyURLopener):
            def prompt_user_passwd(self, host, realm):
                return username, password
    return OpenerWithAuth().retrieve(url, filename, reporthook, data)

class DownloaderThread(QtCore.QThread):
    fileDownloaded = QtCore.pyqtSignal()
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.url = ""
        self.destination = ""
        self.username = False
        self.password = False
        self.backend = "python"
    def setUrl(self, url):
        self.url = url
    def setDestination(self, destination):
        self.destination = destination
#    def exec_(self):
#        urlretrieve(self.url, self.destination)
    def run(self):
        command = ""
        if self.backend == "aria2":
            command = "aria2c --dir='%s'" % (os.path.dirname(unicode(self.destination)))
            if self.username and self.username != "":
                command = "%s --http-user='%s'" % (command, unicode(self.username))
                if self.password and self.password != "":
                    command = "%s --http-passwd='%s'" % (command, unicode(self.password))
            command = "%s '%s'" % (command, self.url)
            system_terminal(command)
        elif self.backend == "axel":
            os.chdir(os.path.dirname(unicode(self.destination)))
            command = "axel"
            command = "%s '%s'" % (command, self.url)
            system_terminal(command)
        else:
            if self.username and self.password:
                urlretrieve_adv(self.url, self.destination, None, None, self.username, self.password)
            else:
                urlretrieve(self.url, self.destination)
        print(command)
        self.username = False
        self.password = False
        self.fileDownloaded.emit()

