#! /usr/bin/env python

def chop(thestring, beginning):
  if thestring.startswith(beginning):
    return thestring[len(beginning):]
  return thestring

def rchop(thestring, ending):
  if thestring.endswith(ending):
    return thestring[:-len(ending)]
  return thestring

def ichop(thestring, beginning):
  if beginning in thestring:
    return thestring[thestring.index(beginning) + len(beginning):]
  return thestring
