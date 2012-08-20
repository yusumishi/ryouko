#! /usr/bin/env python

files = ["extensions/*", "translations/*", "icons/*", "*.*"]

import os, sys, shutil
from distutils.core import setup

app_lib = os.path.dirname(os.path.realpath(__file__))
app_info = os.path.join(app_lib, "ryouko_lib", "info.txt")
app_version = '0.6.5'
if os.path.exists(app_info):
    readVersionFile = open(app_info, "r")
    metadata = readVersionFile.readlines()
    readVersionFile.close()
    if len(metadata) > 0:
        app_version = metadata[0].rstrip("\n")

if "include-nonfree" in sys.argv:
    nf = os.path.join(app_lib, "extensions-nonfree")
    i = os.listdir(nf)
    for fname in i:
        try: shutil.copy2(os.path.join(nf, fname), os.path.join(app_lib, "ryouko_lib", "extensions"))
        except: print("Error in copying file " + fname)

if not "install-singleuser" in sys.argv:
    setup(
        name = 'ryouko',
        version = app_version,
        description = 'PyQt4 Web browser',
        long_description = """Ryouko is a basic PyQt4 Web browser. It was coded for fun and is not intended for serious usage, but it should be capable of fulfilling very basic browsing needs.""",
        scripts = ['ryouko'],
        packages = ['ryouko_lib'],
        package_data = {'ryouko_lib' : files },
        author = 'Daniel Sim',
        author_email =  'foxhead128@gmail.com',
        url = "http://sourceforge.net/projects/ryouko/",
        license = "MIT"
    )

    if sys.platform.startswith("linux") and "install" in sys.argv:
        stdout_handle = os.popen("ryouko --icons")
        icons = stdout_handle.read().replace("\n", "")
        f = open(os.path.join("/", "usr", "share", "applications", "ryouko.desktop"), "w")
        f.write("""[Desktop Entry]
Name=Ryouko
GenericName=Web Browser
Comment=Simple PyQt4 Web Browser

Icon=""" + os.path.join(icons, "logo.svg") + """

Type=Application
Categories=Network;

Exec=ryouko %F
StartupNotify=false
Terminal=false
MimeType=text/html;text/webviewhtml;text/plain;image/jpeg;image/png;image/bmp;image/x-windows-bmp;image/gif;""")
        f.close()

else:
    if os.path.exists(os.path.join(os.path.expanduser("~"), "ryouko")):
        shutil.rmtree(os.path.join(os.path.expanduser("~"), "ryouko"))
    shutil.copytree(app_lib, os.path.join(os.path.expanduser("~"), "ryouko"))
    if not os.path.exists(os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "network")):
        os.makedirs(os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "network"))
    f = open(os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "network", "ryouko.desktop"), "w")
    f.write("""[Desktop Entry]
Name=Ryouko
GenericName=Web Browser
Comment=Simple PyQt4 Web Browser

Icon=""" + os.path.join(os.path.expanduser("~"), "ryouko", "ryouko_lib", "icons", "logo.svg") + """

Type=Application
Categories=Network;

Exec=""" + os.path.join(os.path.expanduser("~"), "ryouko", "ryouko") + """ %F
StartupNotify=false
Terminal=false
MimeType=text/html;text/webviewhtml;text/plain;image/jpeg;image/png;image/bmp;image/x-windows-bmp;image/gif;""")
    f.close()
    if os.path.exists(os.path.join(os.path.expanduser("~"), "bin", "ryouko")):
        os.remove(os.path.join(os.path.expanduser("~"), "bin", "ryouko"))
    elif not os.path.isdir(os.path.join(os.path.expanduser("~"), "bin")):
        os.makedirs(os.path.join(os.path.expanduser("~"), "bin"))
    os.system("ln -s \"" + os.path.join(os.path.expanduser("~"), "ryouko", "ryouko") + "\" \"" + os.path.join(os.path.expanduser("~"), "bin", "ryouko") + "\"")

if "include-nonfree" in sys.argv:
    nf = os.path.join(app_lib, "extensions-nonfree")
    i = os.listdir(nf)
    for fname in i:
        try: os.remove(os.path.join(app_lib, "ryouko_lib", "extensions", fname))
        except: print("Error in copying file " + fname)
