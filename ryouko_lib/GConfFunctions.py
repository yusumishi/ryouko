#! /usr/bin/env python

try:
    import gconf
except:
    def get_key(key):
        return ""
    def set_key(key, val):
        do_nothing()
else:
    def get_key(key):
        client = gconf.client_get_default()
        string = client.get_string(key)
        del client
        return string
    def set_key(key, val):
        client = gconf.client_get_default()
        client.set_string(key, str(val))
