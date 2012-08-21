#! /usr/bin/env python

from __future__ import print_function
import os.path
from os import chdir
from PyQt4 import QtCore
from SimpleHTTPServer import SimpleHTTPRequestHandler
import BaseHTTPServer

class ServerThread(QtCore.QThread):
    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.url = ""
        self.directory = ""
    def setDirectory(self, directory):
        self.directory = directory
    def run(self):
        if os.path.isdir(self.directory):
            chdir(self.directory)
            HandlerClass = SimpleHTTPRequestHandler
            ServerClass  = BaseHTTPServer.HTTPServer
            Protocol     = "HTTP/1.0"

            port = 8000
            server_address = ('127.0.0.1', port)

            HandlerClass.protocol_version = Protocol
            httpd = ServerClass(server_address, HandlerClass)

            sa = httpd.socket.getsockname()
            print("Serving HTTP on", sa[0], "port", sa[1], "...")
            httpd.serve_forever()
