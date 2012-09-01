#! /usr/bin/env python

files = ["extensions/*", "translations/*", "icons/*", "*.*"]

import os, sys, shutil
from distutils.core import setup

app_name = "ryouko"
target_dir = os.path.join(os.path.expanduser("~"), ".ryouko-data", app_name)
app_lib = os.path.dirname(os.path.realpath(__file__))
app_info = os.path.join(app_lib, "ryouko_lib", "info.txt")
app_version = '0.6.5'
if os.path.exists(app_info):
    readVersionFile = open(app_info, "r")
    metadata = readVersionFile.readlines()
    readVersionFile.close()
    if len(metadata) > 0:
        app_version = metadata[0].rstrip("\n")

if not "install-singleuser" in sys.argv:# and not "add-nonfree" in sys.argv and not "remove-nonfree" in sys.argv and not "include-nonfree" in sys.argv:
    setup(
        name = app_name,
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
        stdout_handle = os.popen(app_name + " --icons")
        icons = stdout_handle.read().replace("\n", "")
        f = open(os.path.join("/", "usr", "share", "applications", app_name + ".desktop"), "w")
        f.write("""[Desktop Entry]
Name=Ryouko
GenericName=Web Browser
Comment=Simple PyQt4 Web Browser

Icon=""" + os.path.join(icons, "logo.svg") + """

Type=Application
Categories=Network;

Exec=""" + app_name + """ %F
StartupNotify=false
Terminal=false
MimeType=text/html;text/webviewhtml;text/plain;image/jpeg;image/png;image/bmp;image/x-windows-bmp;image/gif;""")
        f.close()

elif "install-singleuser" in sys.argv:
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    shutil.copytree(app_lib, target_dir)
    if not os.path.exists(os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "network")):
        os.makedirs(os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "network"))
    f = open(os.path.join(os.path.expanduser("~"), ".local", "share", "applications", "network", app_name + ".desktop"), "w")
    f.write("""[Desktop Entry]
Name=Ryouko
GenericName=Web Browser
Comment=Simple PyQt4 Web Browser

Icon=""" + os.path.join(os.path.expanduser("~"), app_name, app_name + "_lib", "icons", "logo.svg") + """

Type=Application
Categories=Network;

Exec=""" + os.path.join(os.path.expanduser("~"), app_name, app_name) + """ %F
StartupNotify=false
Terminal=false
MimeType=text/html;text/webviewhtml;text/plain;image/jpeg;image/png;image/bmp;image/x-windows-bmp;image/gif;""")
    f.close()
    if os.path.exists(os.path.join(os.path.expanduser("~"), "bin", app_name)):
        os.remove(os.path.join(os.path.expanduser("~"), "bin", app_name))
    elif not os.path.isdir(os.path.join(os.path.expanduser("~"), "bin")):
        os.makedirs(os.path.join(os.path.expanduser("~"), "bin"))
    os.system("ln -s \"" + os.path.join(target_dir, app_name) + "\" \"" + os.path.join(os.path.expanduser("~"), "bin", app_name) + "\"")

if "--help" in sys.argv or "-h" in sys.argv:
    print("Ryouko-specific commands:\n")
    print("  setup.py install-singleuser\n                      On Linux, this installs Ryouko to ~/ryouko")