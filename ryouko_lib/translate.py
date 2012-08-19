#! /usr/bin/env python3

# LICENSING:
# This program is free software; you may redistribute and modify it under the
# terms of the following MIT License:

## START OF LICENSE ##
"""
Copyright (c) 2012 Daniel Sim (foxhead128)

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

import os.path
import locale
import sys
from json import load, loads

if sys.version_info[0] >= 3:
    def unicode(data):
        return str(data)

class TranslationManager():
    def __init__(self, directory = ""):
        self.directory = directory
        self.translationStrings = {}
        self.setDefaultTranslation("en_US")
    def setDirectory(self, path):
        if os.path.exists(path) and os.path.isdir(path):
            self.directory = path
            return True
        else:
            return False
    def setDefaultTranslation(self, tr):
        self.defaultTranslation = tr
        translationFile = os.path.join(self.directory, self.defaultTranslation + ".json")
        if os.path.exists(translationFile):
            f = open(translationFile, "r")
            newTranslationStrings = f.read()
            f.close()
            try: newTranslationStrings = loads(newTranslationStrings)
            except: newTranslationStrings = {}
            for key in newTranslationStrings:
                self.translationStrings[key] = newTranslationStrings[key]
    def loadTranslation(self, tr = None):
        if tr == None:
            tr = os.path.join(self.directory, unicode(locale.getdefaultlocale()[0]) + ".json")
        if os.path.exists(tr):
            f = open(tr, "r")
            newTranslationStrings = f.read()
            f.close()
            #newTranslationStrings = newTranslationStrings.replace('\n', ' ')
            try: newTranslationStrings = loads(newTranslationStrings)
            except: newTranslationStrings = {}
            if not type(newTranslationStrings) is dict:
                self.loadTranslation(os.path.join(self.directory, unicode(newTranslationStrings) + ".json"))
            else:
                for key in newTranslationStrings:
                    self.translationStrings[key] = newTranslationStrings[key]
    def tr(self, key):
        try: self.translationStrings[key]
        except:
            try: self.translationStrings[key] = unicode(key)
            except:
                try: self.translationStrings[key] = key
                except:
                    self.translationStrings[key] = "FAIL"
        return unicode(self.translationStrings[key])