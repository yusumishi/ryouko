#! /usr/bin/env python

import os

app_lib = os.path.dirname(os.path.realpath(__file__))
dependencies = ["python-qt4", "python"]

def do_nothing():
    return

def main():
    os.chdir(app_lib)
    ok = True
    meh = False
    for package in dependencies:
        stdout_handle = os.popen("dpkg-query -W -f='${Status}' " + package)
        value = stdout_handle.read()
        if not "not-installed" in value and "installed" in value:
            do_nothing()
        else:
            ok = False
            break
    if ok == True:
        os.system("(gksudo python \"" + os.path.join(app_lib, "setup.py") + "\" install) && sudo rm -rf \"" + os.path.join(app_lib, "build") + "\" && zenity --info --text='Ryouko was successfully installed. For best results, it is recommended that you install python-notify and python-gi as well.'")
    else:
        l = ""
        for package in dependencies:
            l = "%s%s " % (l, package)
        l = l.rstrip(" ")
        os.system("zenity --info --text='One of the following dependencies was not met:\n" + l + "\n\nPlease install the required dependencies before installing Ryouko.'")

if __name__ == "__main__":
    main()
