#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-

import socket
import urllib, re, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import HTMLParser
import CommonFunctions
import simplejson as json
from helpers import * 


from locale import getdefaultlocale
from urllib2 import Request, urlopen, URLError, HTTPError

common = CommonFunctions
socket.setdefaulttimeout(10)


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

def play(url):
    url = "http://stream-high.kmih.org:8000/;stream.nsv"
    #item = xbmcgui.ListItem(path = url)
    #xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER).play(url, item)

    #item = xbmcgui.ListItem(path = url)
    #xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    
    try:
        item = xbmcgui.ListItem(path = url)
        xbmc.Player().play(url, item)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        return False
    else:
        print "OK playing"
        
# def get_play(url, name):
#   xbmc.output('>>> get_play(%s, %s)' % (url, name))
#   #use_wma = True
#   #use_mp3 = True
# 
#   playList = xbmc.PlayList(xbmc.PLAYLIST_MUSIC)
#   playList.clear()
# 
# # if use_wma:
#   #wma_url = url.replace('port_playmp3','port_playwma')
#   wma0 = getURL(url)
#   if wma0 != None:
#       wma1 = re.compile('<param name="URL" value="(.*?)">').findall(wma0)
#       if len(wma1) > 0:
# 
#           #xbmc.Player().play(wma1[0].replace('&amp;','&'))
# 
# 
#           wma2 = getURL(wma1[0].replace('&amp;','&'))
#           if wma2 != None:
#               wma3 = re.compile('<ref href = "(.*?)"/>').findall(wma2)
#               if len(wma3) > 0:
#                   x = 1
#                   stacked_url = ''
#                   for wma_purl in reversed(wma3):
#                       item = xbmcgui.ListItem('%s [WMA Server %s])'%(name,x),iconImage=play_thumb,thumbnailImage=play_thumb)
#                       item.setInfo(type='music',infoLabels={'title':name,'artist': '101.RU'})
#                       playList.add(wma_purl, item)
#                   xbmc.Player().play(playList)


#   if use_mp3:
#       mp3_url = url.replace('port_playwma','port_playmp3')
#       mp0 = getURL(mp3_url)
#       if mp0 != None:
#           mp1 = re.compile('"pl":"(.*?)"').findall(mp0)
#           if len(mp1) > 0:
#               cur_mpu = mp1[0].replace('|','&')
#               mp2 = getURL(cur_mpu, 'http://101.ru/101player/uppod7.swf')
#               mp3 = re.compile('"file":"(.*?)"').findall(mp2)
#               if len(mp3) > 0:
#                   x = 1
#                   for streamer in mp3:
#                       item = xbmcgui.ListItem('Serv %s. %s (MP3)'%(x,name),iconImage=play_thumb,thumbnailImage=play_thumb)
#                       item.setInfo(type='music',infoLabels={'title':name,'artist': '101.RU'})
#                       xbmcplugin.addDirectoryItem(handle, streamer, item)
#   xbmcplugin.endOfDirectory(handle)


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
    play(url)
elif mode == 'onlineradio':
    onlineradio(url, category)
