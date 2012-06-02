#!/usr/bin/env python
# -*- coding: utf-8 -*-

import gtk, os, re, urllib2, fnmatch

from aptsources.distinfo import DistInfo
from config import *

def Dummy(signaled, class_id):
    pass

def LocaleList(class_id, supported, current):
    localecount = 0
    localeactive = 0
    localelist = []
    with open(supported, 'r') as supportedlocales:
        for item in supportedlocales:
            localecode = item.split()
            localelist.append(localecode[0])
            if localecode[0].upper().replace('-','') == current.upper().replace('-',''):
                localeactive = localecount
            localecount += 1

    return localelist, localeactive

def CodenameList(class_id, dist, db):
    codenamelist = []
    codenameactive = 0
    udist = dist.get_active_text().title()
    d = DistInfo(udist, db)

    for template in d.templates:
        if not template.name in codenamelist:
            codenamelist.append(template.name)

    return codenamelist, codenameactive

def SectionList(class_id, dist):
    text = dist.get_active_text()
    exec "sectionlist = "+text+"_sections"
    return sectionlist

def listdirfullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]

def is_valid_url(url):
    regex = re.compile(
        r'^(http|ftp|file):///?'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|[a-zA-Z0-9-]*|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return regex.search(url)

def DownloadProgress(bar, pulse, percent):
    if pulse:
        bar.pulse()
    else:
        if percent >= 1: percent = 1
        bar.set_fraction(percent)
    return True
    
def CleanTempDir(tempdir):
    if not os.path.exists(tempdir):
        mktempdir = os.mkdir(tempdir)

    for path in os.listdir(tempdir):
        if os.path.isfile(tempdir+path) and fnmatch.fnmatch(tempdir+path, '*.gz'):
            os.unlink(tempdir+path)

    return True

class HeadRequest(urllib2.Request):
    def get_method(self):
        return "HEAD"
        
def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
