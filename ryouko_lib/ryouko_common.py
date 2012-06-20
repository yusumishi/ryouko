#! /usr/bin/env python

# This file is released under the terms of the following MIT license:

## START OF LICENSE ##
"""
Copyright (c) 2012 Daniel Sim
Portions of the code are copyright (c) 2011 roberto.alsina

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
## END OF LICENSE ##

def do_nothing():
    return

import os.path, sys, json
from subprocess import Popen, PIPE

try:
    filename = __file__
except:
    __file__ = sys.executable
else:
    del filename
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)

if sys.version_info[0] >= 3:
    def unicode(data):
        return str(data)
    def unichr(data):
        return chr(data)
    from html.entities import name2codepoint
    from html.parser import HTMLParser
else:
    import HTMLParser
    from htmlentitydefs import name2codepoint

import re

try: from urllib.parse import unquote, quote
except ImportError:
    try: from urllib import unquote, quote
    except:
        do_nothing()

from xml.sax.saxutils import escape, quoteattr

try: from urllib.request import urlopen
except ImportError:
    try: from urllib2 import urlopen
    except:
        do_nothing()

_entity_re = re.compile(r'&(?:(#)(\d+)|([^;]+));')

def get_mimetype(filename):
    try: f = urlopen("file://" + metaunquote(filename).replace("file://",""))
    except:
        print("Error! Something went wrong!")
        return None
    else:
        return f.headers['content-type']

def shred_directory(directory):
    if os.path.isdir(directory):
        d = os.listdir(directory)
        for f in d:
            fname = os.path.join(directory, f)
            if sys.platform.startswith("linux") and not os.path.isdir(fname):
                os.system("shred -v \"" + fname + "\"")
            try: os.remove(fname)
            except:
                do_nothing()

def _repl_func(match):
    if match.group(1): # Numeric character reference
        return unichr(int(match.group(2)))
    else:
        return unichr(name2codepoint[match.group(3)])

def handle_html_entities(data):
    return unescape(_entity_re.sub(_repl_func, data))
    
def metaunquote(data):
    return handle_html_entities(unquote(data))

def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
      keep &amp;, &gt;, &lt; in the source code.
   from Fredrik Lundh
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            print("Value error!")
            pass
      else:
         # named entity
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               print(text[1:-1])
               text = unichr(name2codepoint[text[1:-1]])
         except KeyError:
            print("Key error!")
            pass
      return text # leave as is
   return re.sub("&#?\w+;", fixup, text)

class SettingsManager():
    def __init__(self, app_profile = os.path.join(os.path.expanduser("~"), ".ryouko-data", "profiles", "default")):
        self.settings = {'openInTabs' : True, 'oldSchoolWindows' : False, 'loadImages' : True, 'jsEnabled' : True, 'storageEnabled' : True, 'pluginsEnabled' : False, 'privateBrowsing' : False, 'backend' : 'qt', 'loginToDownload' : False, 'adBlock' : False}
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
