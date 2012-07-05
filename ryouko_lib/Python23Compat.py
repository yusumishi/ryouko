#! /usr/bin/env python

import sys

if sys.version_info[0] >= 3:
    def unicode(data):
        return str(data)
