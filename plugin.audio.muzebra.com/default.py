#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.2
# -*- coding: utf-8 -*-


import urllib, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

from helpers import * 

common = CommonFunctions

BASE_URL = 'http://muzebra.com/'
handle = int(sys.argv[1])


Addon = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
addon_cache = xbmc.translatePath( Addon.getAddonInfo( "profile" ) )

Language = Addon.getLocalizedString

def main():
    category = Language(1000)
    uri = sys.argv[0] + '?mode=onlineradio'
    uri += '&url='  + urllib.quote_plus('http://muzebra.com/radio/air/')
    uri += '&category=' + 'Online radio'

    item = xbmcgui.ListItem(category, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {'title': category, 'album': BASE_URL, 'genre': category, 'artist': 'muzebra.com'})
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)
    xbmcplugin.endOfDirectory(handle, True)

def onlineradio(url, category):
    page = common.fetchPage({"link": url})
    
    if page["status"] == 200:
        playlist = common.parseDOM(page["content"], "ul", attrs = { "class":"playlist" })
        links = common.parseDOM(playlist, "a", attrs = { "class":"info" }, ret="data-url") 
        titles = common.parseDOM(playlist, "a", attrs = { "class":"info" })
        
        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=play'
            uri += '&url='  + urllib.quote_plus(links[i])
            
            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': title, 'album': title, 'genre': category, 'artist': title})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)
    
    xbmcplugin.endOfDirectory(handle, True)


def play_url(url):
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(handle, True, item)


params = get_params()
url  =  None
mode =  None
title =  None
category = None
thumbnail = None

try:
    mode=params['mode']
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    category=params['category']
except: pass
try:
    title=params['title']
except: pass
try:
    thumbnail=urllib.unquote_plus(params['thumbnail'])
except: pass

if mode == None:
    main()
elif mode == 'play':
    play_url(url)
elif mode == 'onlineradio':
    onlineradio(url, category)
