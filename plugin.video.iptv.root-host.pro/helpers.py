#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-

import os, sys, urllib2, socket
import xbmcgui, xbmcaddon, xbmcplugin

import HTMLParser
import  CommonFunctions

common = CommonFunctions
common.plugin = "plugin.video.iptv.root-host.pro"

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv.root-host.pro')
__language__ = __addon__.getLocalizedString
addon_icon    = __addon__.getAddonInfo('icon')
addon_path    = __addon__.getAddonInfo('path')

# TODO Replace by commonParse function
def unescape(entity, encoding):
    if encoding == 'utf-8':
        return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
    elif encoding == 'cp1251':
        return HTMLParser.HTMLParser().unescape(entity).decode(encoding).encode('utf-8')

def check_url(host):
    print "***** HOST " +host

    try:
        response = urllib2.urlopen(host, None, 3)
        print '*** ' + response.info()['Content-type']
        print response.info()
        stream = {'url':response.geturl(), 'mimetype':response.info()['Content-type']}
    except urllib2.HTTPError, e:
        print "***** Oops, HTTPError ", str(e.code)
        if e.code == 401:
            print "401 Unauthorized"
        return False
    except urllib2.URLError, e:
        print "***** Oops, URLError", str(e.args)
        if not str(e.args).find("rtsp") == -1:
            return stream
            pass
    except socket.timeout, e:
        print "***** Oops timed out! ", str(e.args)
        return False
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return []
    else:
        return stream

def xbmcItem(mode, url, title, category=False):
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url
    if title: uri += '&title=' + title
    if category: uri += '&category=' + category

    item = xbmcgui.ListItem(title, iconImage=addon_icon, thumbnailImage=addon_icon)
    item.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle, uri, item, True)

#['http://www.abload.de/img/7mqwj.png', '\xd0\xa8\xd0\xb0\xd0\xbd\xd1\x81\xd0\xbe\xd0\xbd \xd0\xa2\xd0\x92', '89', 'Music']
def xbmcPlayableItem(mode, image, title, url, category):
    uri = sys.argv[0] + '?mode='+ mode
    uri += '&url=' + url
    #uri += '&image=' + image
    uri += '&title=' + title 
    #uri += '&category=' + category

    item = xbmcgui.ListItem(title, iconImage=image, thumbnailImage=image)
    item.setInfo(type='Video', infoLabels = {'title': title, 'category':category})
    item.setProperty('IsPlayable', 'true')
    xbmcplugin.addDirectoryItem(handle, uri, item)

def xbmcContextMenuItem(item, action, label, url, title):
    script = "special://home/addons/plugin.video.iptv5.ts9.ru/contextmenu.py"
    params = action + "|%s"%url + "|%s"%title
    runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
    item.addContextMenuItems([(label, runner)])
