#! /usr/bin/env python

import os, sys
from subprocess import Popen, PIPE

terminals=[ ["terminator",      "-x "],
            ["sakura",          "--execute="],
            ["roxterm",         "--execute "],
            ["xfce4-terminal",  "--command="],
            ["Terminal",  "--command="],
            ["gnome-terminal",  "--command="],
            ["idle3",           "-r "],
            ["xterm",           ""],
            ["konsole",         "-e="] ]

open_commands=["xdg-open", "gnome-open", "kde-open", "mate-open"]

def readTerminalOutput(command):
    return read_terminal_output(command)

def read_terminal_output(command):
    stdout_handle = os.popen(command)
    value = stdout_handle.read().rstrip("\n")
    return value

def systemTerminal(command):
    system_terminal(command)

def system_terminal(command):
    location = False
    for app in terminals:
        location=Popen(["which", app[0]], stdout=PIPE).communicate()[0]
        if location:
            os.system(app[0]+' '+app[1]+"\""+command+"\"")
            break
    if not location:
        os.system(command)

def system_open(location):
    if sys.platform.startswith("linux"):
        a=False
        for app in open_commands:
            a=Popen(["which", app], stdout=PIPE).communicate()[0]
            if a:
                expression = app + " \"" + unicode(location) + "\" & echo \"\" >> /dev/null"
                break
    elif sys.platform.startswith("win"):
        expression = "start " + unicode(location)
    elif "darwin" in sys.platform:
        expression = "open \"" + unicode(location) + "\" & echo \"\" >> /dev/null"
    else:
        expression = ""
    print(expression)
    os.system(expression)