#! /usr/bin/env python

import os.path, sys

try:
    __file__
except:
    __file__ = sys.executable
app_lib = os.path.dirname(os.path.realpath(__file__))

import translate

trManager = translate.TranslationManager()
trManager.setDirectory(os.path.join(app_lib, "translations"))
trManager.loadTranslation()

def tr(key):
    return trManager.tr(key)
