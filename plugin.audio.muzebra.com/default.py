#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.2
# -*- coding: utf-8 -*-


import urllib, urllib2, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

from helpers import * 

common = CommonFunctions

BASE_URL = 'http://muzebra.com/'
MEDIA_URL = 'http://media.justmuz.com/t/'
handle = int(sys.argv[1])


Addon = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
addon_cache = xbmc.translatePath( Addon.getAddonInfo( "profile" ) )

Language = Addon.getLocalizedString

def main():
    radio = Language(1001)
    uri = construct_url('onlineradio', 'http://muzebra.com/radio/air/', '', radio)

    item = xbmcgui.ListItem(radio, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {'title': radio, 'album': BASE_URL, 'genre': radio, 'artist': 'muzebra.com'})
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    ru_charts = Language(2001)
    uri = construct_url('charts', 'http://muzebra.com/charts/', '', ru_charts)

    item = xbmcgui.ListItem(ru_charts, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {'title': ru_charts, 'album': BASE_URL, 'genre': ru_charts, 'artist': 'muzebra.com'})
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)
 
    en_charts = Language(2002)
    uri = construct_url('charts', 'http://muzebra.com/charts/en/', '', en_charts)

    item = xbmcgui.ListItem(en_charts, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {'title': en_charts, 'album': BASE_URL, 'genre': en_charts, 'artist': 'muzebra.com'})
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

def charts(url, category):
    page = common.fetchPage({"link": url})
    
    if page["status"] == 200:
        playlist = common.parseDOM(page["content"], "ul", attrs = { "class":"playlist" })
        links = common.parseDOM(playlist, "a", attrs = { "class":"info" }, ret="data-aid") 
        titles = common.parseDOM(playlist, "a", attrs = { "class":"info" })
        
        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=play_mp3'
            uri += '&url='  + urllib.quote_plus(links[i])
            
            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': title, 'album': title, 'genre': category, 'artist': title})
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)
    
    xbmcplugin.endOfDirectory(handle, True) 
    
def getURL(url):
	req = urllib2.Request(url)
	req.add_header('User-Agent', 'Opera/10.60 (X11; openSUSE 11.3/Linux i686; U; ru) Presto/2.6.30 Version/10.60')
	req.add_header('Accept', 'text/html, application/xml, application/xhtml+xml, */*')
	req.add_header('Accept-Language', 'ru,en;q=0.9')
	response = urllib2.urlopen(req)
	link=response.read()
	response.close()
	return link
	
def play_mp3(url):
    
    mp3_url = MEDIA_URL + url + '/'
    
    #content = getURL(mp3_url)
    #item = xbmcgui.ListItem(path = url)
    #print url
    #xbmc.Player.play(url)
    
    page = common.fetchPage({"link": 'http://media.justmuz.com/t/9kgbpcp5lvaj_a625de3a4e/'})

    print page
    #item = xbmcgui.ListItem(path = urllib.quote_plus("http://media.justmuz.com/t/9kgbpcp5lvaj_a625de3a4e/"))
    #xbmcplugin.setResolvedUrl(handle, True, item)
    
    #xbmc.Player().play(urllib.quote_plus("http://media.justmuz.com/t/9kgbpcp5lvaj_a625de3a4e/"))
        
def play_stream(url):
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
elif mode == 'play_stream':
    play_stream(url)
elif mode == 'play_mp3':
    play_mp3(url)
elif mode == 'onlineradio':
    onlineradio(url, category)
elif mode == 'charts':
    charts(url, category)
