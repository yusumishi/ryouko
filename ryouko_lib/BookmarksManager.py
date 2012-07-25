#! /usr/bin/env python

import os, sys
from PyQt4 import QtCore

class BookmarksManager(QtCore.QObject):
    bookmarksChanged = QtCore.pyqtSignal()
    userLinksChanged = QtCore.pyqtSignal(str)
    def __init__(self, app_links, parent=None):
        super(BookmarksManager, self).__init__()
        self.parent = parent
        self.bookmarks = []
        self.app_links = app_links
        self.reload_()
    def setDirectory(self, app_links):
        self.app_links = app_links
    def reload_user_links(self, app_links):
        links = []
        if os.path.isdir(app_links):
            l = os.listdir(app_links)
            links = []
            for fname in l:
                f = os.path.join(app_links, fname)
                fi = open(f, "r")
                contents = fi.read()
                fi.close()
                contents = contents.rstrip("\n")
                links.append([contents, fname.rstrip(".txt")])
            links.sort()
            global user_links
            user_links = ""
            for link in links:
                user_links = "%s<a href=\"%s\">%s</a> \n" % (user_links, link[0], link[1])
            self.userLinksChanged.emit(user_links)
            return user_links
    def reload_(self):
        self.bookmarks = []
        if not os.path.isdir(self.app_links):
            os.mkdir(self.app_links)
        if os.path.isdir(self.app_links):
            links = os.listdir(self.app_links)
            for fname in links:
                path = os.path.join(self.app_links, fname)
                f = open(path)
                link = f.read()
                f.close()
                link = link.replace("\n", "")
                self.bookmarks.append({"name": fname.rstrip(".txt"), "url": link})
            if sys.version_info[0] < 3:
                self.bookmarks.sort()
            self.bookmarksChanged.emit()
    def add(self, url, name):
        f = open(os.path.join(self.app_links, name + ".txt"), "w")
        f.write(url)
        f.close()
        self.reload_()
        self.bookmarksChanged.emit()
    def removeByName(self, path):
        path = os.path.join(self.app_links, path)
        if os.path.exists(path):
            os.remove(path)
        if os.path.exists(path + ".txt"):
            os.remove(path + ".txt")
        self.reload_()
        self.reload_user_links(self.app_links)
        self.bookmarksChanged.emit()
