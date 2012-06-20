cd /d %~dp0
C:\Python27\Scripts\cxfreeze.bat "ryouko" --target-dir=".\" --base-name="Win32GUI" --include-modules="PyQt4.QtCore,PyQt4.QtGui,PyQt4.QtWebKit,PyQt4.QtNetwork,json,string,shutil,urllib,time,datetime,os,sys,subprocess,HTMLParser,xml.sax.saxutils" --exclude-modules="ryouko_lib,PyQt4.uic" --icon="ryouko_lib\icons\ryouko.ico"
C:\Python27\python.exe "do-finish-compile-windows.py"
