ABOUT RYOUKO:
Ryouko is a simple Web browser coded in Python/PyQt4. It is an official fork of the C++/Qt4-based Web browser, Haruna2 (http://foxhead128.deviantart.com/art/Haruna2-245283932).

AUTHORS:
For authors, see AUTHORS.txt.

LICENSING TERMS:
For licensing terms, see LICENSE.txt.

RUNNING RYOUKO:
Ryouko requires Python 2.x and PyQt4 to be installed. Once that's done, run the ryouko.py script from the command-line (or in Linux, you can probably just double-click it after giving it executable permissions).

COMPILING ON WINDOWS:
Ryouko is compiled on Windows by compiling the extension-less script named "ryouko" using cx_Freeze with the following options:

--base-name="Win32GUI" --include-modules="PyQt4.QtCore,PyQt4.QtGui,PyQt4.QtWebKit,PyQt4.QtNetwork,json,string,shutil,urllib,time,datetime,os,sys,subprocess,HTMLParser,xml.sax.saxutils" --exclude-modules="ryouko_lib,PyQt4.uic" --icon="\path\to\ryouko\root\folder\ryouko_lib\icons\ryouko.ico"

This should create a folder called "dist" (no quotes); from now on, this folder will be referred to as the "target folder". Once this has been done, you'll need to create a file called "qt.conf" (no quotes) in the target folder that contains the following text:

[Paths]
Prefix = ./PyQt4
Binaries = ./PyQt4


Once this is done, create a new folder called "PyQt4" (no quotes) inside the target folder. Then create a folder named "plugins" inside the new folder. From your PyQt4 installation (usually C:\PythonXX\Lib\site-packages\PyQt4), open the "plugins" folder and copy the folder named "imageformats" into the folder "<target folder>/PyQt4/plugins" Lastly, you'll have to copy the entire folder named "ryouko_lib" from Ryouko's root folder into the target folder. To run, simply double-click ryouko.exe.