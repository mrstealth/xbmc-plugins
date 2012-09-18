#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.4
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-

import os, sys
import xbmcgui, xbmcaddon, xbmcplugin

import HTMLParser
import  CommonFunctions

common = CommonFunctions
common.plugin = "plugin.video.iptv5.ts9.ru"

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
__language__ = __addon__.getLocalizedString
addon_icon    = __addon__.getAddonInfo('icon')
addon_path    = __addon__.getAddonInfo('path')

# TODO Replace by commonParse function
def unescape(entity, encoding):
    if encoding == 'utf-8':
        return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
    elif encoding == 'cp1251':
        return HTMLParser.HTMLParser().unescape(entity).decode(encoding).encode('utf-8')

def check_url(url):
    if not url.find("rtsp") == -1: # skip rtsp check
        print "*** Skip rtsp check for " + url
        return True
    try:
        response = urllib2.urlopen(url, None, 1)
    except urllib2.HTTPError, e:
        print "***** Oops, HTTPError ", str(e.code)
        return False
    except urllib2.URLError, e:
        print "***** Oops, URLError", str(e.args)
        return False
    except socket.timeout, e:
        print "***** Oops timed out! ", str(e.args)
        return False
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return False
    else:
        return True

def xbmcItem(mode, url, title, icon=False, category=False):
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url
    if not icon: icon = addon_icon
    if category: uri += '&category=' + category

    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
    item.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle, uri, item, True)


def xbmcPlayableItem(mode, title, url, action):
    print action
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url

    item = xbmcgui.ListItem(title, iconImage=addon_icon, thumbnailImage=addon_icon)
    item.setInfo(type='Video', infoLabels = {'title': title})
    item.setProperty('IsPlayable', 'true')

    if action == 'add':
        label = __language__(1001)
    else:
        label = __language__(1002)
        
    xbmcContextMenuItem(item, action, label, url, title)
    xbmcplugin.addDirectoryItem(handle, uri, item)


def xbmcContextMenuItem(item, action, label, url, title):
    script = "special://home/addons/plugin.video.iptv5.ts9.ru/contextmenu.py"
    params = action + "|%s"%url + "|%s"%title
    runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
    item.addContextMenuItems([(label, runner)])
