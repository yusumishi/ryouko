ABOUT RYOUKO:
Ryouko is a simple Web browser coded in Python/PyQt4. It is an official fork of the C++/Qt4-based Web browser, Haruna2 (http://foxhead128.deviantart.com/art/Haruna2-245283932).

AUTHORS:
For authors, see AUTHORS.txt.

LICENSING TERMS:
For licensing terms, see LICENSE.txt.

RUNNING RYOUKO:
Ryouko requires Python 2.x and PyQt4 to be installed. Once that's done, run the ryouko.py script from the command-line (or in Linux, you can probably just double-click it after giving it executable permissions).

COMPILING ON WINDOWS:
Ryouko is compiled on Windows by compiling the extension-less script named "ryouko" using the following options:
--base-name="Win32GUI" --include-modules="PyQt4.QtCore,PyQt4.QtGui,PyQt4.QtWebKit,PyQt4.QtNetwork,json,pickle,urllib,time,datetime,os,sys,subprocess,HTMLParser,xml.sax.saxutils" --exclude-modules="ryouko_lib,PyQt4.uic" --icon="/path/to/ryouko/root/folder/ryouko_lib/icons/logo.ico"
