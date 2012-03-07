#!/usr/bin/env python

# This is a modified version of the arietta module from Akane. It is
# hereby released under the terms of the GNU LGPL version 2.1. See
# lgpl-2.1-ryoukodesu.txt and/or
# http://www.gnu.org/licenses/lgpl-2.1.html for more details.

def do_nothing():
    return

import os.path
import sys

try:
    filename = __file__
except:
    __file__ = sys.executable
else:
    del filename
app_lib = os.path.join(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(app_lib)

if sys.version_info[0] >= 3:
    def unicode(data):
        return str(data)
    def unichr(data):
        return chr(data)
# Commented out from the original module:
#    import stagger
#    from html.parser import HTMLParser
    from html.entities import name2codepoint
else:
# Commented out from the original module:
#    import id3
#    import HTMLParser
    from htmlentitydefs import name2codepoint

import re

try: from urllib.parse import unquote, quote
except ImportError:
    try: from urllib import unquote, quote
    except:
        do_nothing()

from xml.sax.saxutils import escape, quoteattr

try: from urllib.request import urlopen
except ImportError:
    try: from urllib2 import urlopen
    except:
        do_nothing()

_entity_re = re.compile(r'&(?:(#)(\d+)|([^;]+));')

def get_mimetype(filename):
    if os.path.exists(metaunquote(filename).replace("file://", "")):
        try: f = urlopen("file://" + metaunquote(filename).replace("file://",""))
        except:
            print("Error! Something went wrong!")
        else:
            return f.headers['content-type']
    else:
        print("Error! File does not exist!")
        return None

def _repl_func(match):
    if match.group(1): # Numeric character reference
        return unichr(int(match.group(2)))
    else:
        return unichr(name2codepoint[match.group(3)])

def handle_html_entities(data):
    return unescape(_entity_re.sub(_repl_func, data))
    
def metaunquote(data):
    return handle_html_entities(unquote(data))

def unescape(text):
   """Removes HTML or XML character references 
      and entities from a text string.
      keep &amp;, &gt;, &lt; in the source code.
   from Fredrik Lundh
   http://effbot.org/zone/re-sub.htm#unescape-html
   """
   def fixup(m):
      text = m.group(0)
      if text[:2] == "&#":
         # character reference
         try:
            if text[:3] == "&#x":
               return unichr(int(text[3:-1], 16))
            else:
               return unichr(int(text[2:-1]))
         except ValueError:
            print("Value error!")
            pass
      else:
         # named entity
         try:
            if text[1:-1] == "amp":
               text = "&amp;amp;"
            elif text[1:-1] == "gt":
               text = "&amp;gt;"
            elif text[1:-1] == "lt":
               text = "&amp;lt;"
            else:
               print(text[1:-1])
               text = unichr(name2codepoint[text[1:-1]])
         except KeyError:
            print("Key error!")
            pass
      return text # leave as is
   return re.sub("&#?\w+;", fixup, text)

# Commented out from the original module:
# The following function scans a file for ID3 tags, using either stagger (if Python 3) or id3 (if Python 2). It then returns a dictionary containing whatever tags it was able to retrieve:
"""def get_tags(path):
    if os.path.exists(metaunquote(path.replace("file://", ""))):
        path = metaunquote(path.replace("file://", ""))
    elif os.path.exists(path.replace("file://", "")):
        path = path.replace("file://", "")
    if os.path.exists(path):
        if sys.version_info[0] >= 3:
            try: tags = stagger.read_tag(metaunquote(path.replace("file://", "")))
            except:
                tags = ""
        title = "(Untitled)"
        artist = "Unknown Artist"
        album = "Unknown Album"
        date = "Unknown"
        genre = "Unknown"
        if sys.version_info[0] >= 3:
            try: tags.title
            except:
                do_nothing()
            else:
                if type(tags.title) is str and tags.title != "":
                    try: title = tags.title
                    except:
                        do_nothing()
            try: tags.artist
            except:
                do_nothing()
            else:
                if type(tags.artist) is str and tags.artist != "":
                    try: artist = tags.artist
                    except:
                        do_nothing()
            try: tags.album
            except:
                do_nothing()
            else:
                if type(tags.album) is str and tags.album != "":
                    try: album = tags.album
                    except:
                        do_nothing()
            try: tags.date
            except:
                do_nothing()
            else:
                if type(tags.date) is str and tags.date != "":
                    try: date = tags.date
                    except:
                        do_nothing()
            try: tags.genre
            except:
                do_nothing()
            else:
                if type(tags.genre) is str and tags.genre != "":
                    try: genre = tags.genre
                    except:
                        do_nothing()
        else:
            path = metaunquote(path.replace("file://", "")).replace("%20", " ")
            try: id3.title(path)
            except:
                do_nothing()
            else:
                if type(id3.title(path)) is unicode and id3.title(path) != "":
                    try: title = id3.title(path)
                    except:
                        do_nothing()
            try: id3.artist(path)
            except:
                do_nothing()
            else:
                if type(id3.artist(path)) is unicode and id3.artist(path) != "":
                    try: artist = id3.artist(path)
                    except:
                        do_nothing()
            try: id3.album(path)
            except:
                do_nothing()
            else:
                if type(id3.album(path)) is unicode and id3.album(path) != "":
                    try: album = id3.album(path)
                    except:
                        do_nothing()
            try: id3.date(path)
            except:
                do_nothing()
            else:
                if type(id3.date(path)) is unicode and id3.date(path) != "":
                    try: date = id3.date(path)
                    except:
                        do_nothing()
            try: id3.genre(path)
            except:
                do_nothing()
            else:
                if type(id3.genre(path)) is unicode and id3.genre(path) != "":
                    try: genre = id3.genre(path)
                    except:
                        do_nothing()
        return {'title' : unicode(title), 'artist' : unicode(artist), 'album' : unicode(album), 'year' : unicode(date), 'date' : unicode(date), 'genre' : unicode(genre)}"""

# Commented out from the original module:
# This is for reading XSPF files:
"""if sys.version_info[0] >= 3:
    class XSPFReader(HTMLParser):
        event_list = []
        event_contents = ""
        tag = ""
        def handle_starttag(self, tag, attrs):
            self.tag = tag
        def handle_startendtag(self, tag, attrs):
            self.tag = tag
            self.attributes = attrs
        def handle_endtag(self, tag):
            self.tag = ""
        def handle_data(self, data):
            if self.tag == "playlist":
                self.playlist = []
            elif self.tag == "location":
                self.playlist.append(data)
else:
    class XSPFReader(HTMLParser.HTMLParser):
        event_list = []
        event_contents = ""
        tag = ""
        def handle_starttag(self, tag, attrs):
            self.tag = tag
        def handle_startendtag(self, tag, attrs):
            self.tag = tag
            self.attributes = attrs
        def handle_endtag(self, tag):
            self.tag = ""
        def handle_data(self, data):
            if self.tag == "playlist":
                self.playlist = []
            elif self.tag == "location":
                self.playlist.append(data)"""
