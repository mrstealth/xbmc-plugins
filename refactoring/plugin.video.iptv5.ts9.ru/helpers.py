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

Addon = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
__settings__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')

# TODO Replace by commonParse function
def unescape(entity, encoding):
    if encoding == 'utf-8':
        return HTMLParser.HTMLParser().unescape(entity).encode(encoding)
    elif encoding == 'cp1251':
        return HTMLParser.HTMLParser().unescape(entity).decode(encoding).encode('utf-8')

def xbmcItem(mode, url, title, icon=False, category=False):
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url
    if not icon: icon = addon_icon
    if category: uri += '&category=' + category

    item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
    item.setProperty('IsPlayable', 'false')
    xbmcplugin.addDirectoryItem(handle, uri, item, True)

def xbmcPlayableItem(mode, title, url):
    uri = sys.argv[0] + '?mode='+ mode + '&url=' + url

    item = xbmcgui.ListItem(title, iconImage=addon_icon, thumbnailImage=addon_icon)
    item.setInfo(type='Video', infoLabels = {'title': title})
    item.setProperty('IsPlayable', 'true')

    xbmcplugin.addDirectoryItem(handle, uri, item, False)

def xbmcContextMenuItem(item, action, label, url, title):
    script = "special://home/addons/plugin.video.iptv5.ts9.ru/contextmenu.py"
    params = action + "|%s"%url + "|%s"%title
    runner = "XBMC.RunScript(" + str(script)+ ", " + params + ")"
    item.addContextMenuItems([(label, runner)])
