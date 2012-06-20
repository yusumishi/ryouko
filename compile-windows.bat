@echo off
cd /d %~dp0
echo This script will compile Ryouko for you! Before you continue, make sure that:
echo 1) Python 2 is installed to C:\Python27.
echo 2) PyQt4 is installed.
echo 3) cx_Freeze is installed.
PAUSE
C:\Python27\Scripts\cxfreeze.bat "ryouko" --target-dir="." --base-name="Win32GUI" --include-modules="PyQt4.QtCore,PyQt4.QtGui,PyQt4.QtWebKit,PyQt4.QtNetwork,json,string,shutil,urllib,time,datetime,os,sys,subprocess,HTMLParser,xml.sax.saxutils" --exclude-modules="ryouko_lib,PyQt4.uic" --icon="ryouko_lib\icons\ryouko.ico" && C:\Python27\python.exe "do-finish-compile-windows.py" && echo Compilation successful! && PAUSE