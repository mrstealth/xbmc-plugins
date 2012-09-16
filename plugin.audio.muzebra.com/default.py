#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.3
# -*- coding: utf-8 -*-


import urllib, urllib2, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions
import simplejson as json
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
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    xbmcplugin.endOfDirectory(handle, True)


def onlineradio(url, category):
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        playlist = common.parseDOM(page["content"], "ul", attrs = { "class":"playlist" })
        links = common.parseDOM(playlist, "a", attrs = { "class":"info" }, ret="data-url")
        titles = common.parseDOM(playlist, "a", attrs = { "class":"info" })

        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=play_stream'
            uri += '&url='  + urllib.quote_plus(links[i])
            uri += '&title='  + title.decode('utf-8')
            uri += '&category='  + category.decode('utf-8')

            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': title, 'genre': category })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)

    xbmcplugin.endOfDirectory(handle, True)


def charts(url, category):
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        playlist = common.parseDOM(page["content"], "ul", attrs = { "class":"playlist" })
        song_ids = common.parseDOM(playlist, "a", attrs = { "class":"info" }, ret="data-aid")

        durations = common.parseDOM(playlist, "div", attrs = { "class":"time" })

        songs = common.parseDOM(playlist, "a", attrs = { "class":"info" })

        title_div = common.parseDOM(playlist, "div", attrs = { "class":"title" })
        songs = common.parseDOM(title_div, "span", attrs = { "class":"name" })
        artists = common.parseDOM(title_div, "a")


        #for i in range(1):
        for i, identifier in enumerate(song_ids):
            uri = sys.argv[0] + '?mode=play_mp3'
            uri += '&aid='  + identifier


            song = songs[i].decode('utf-8')
            artist = artists[i].decode('utf-8')
            title = artist + "-" + song

            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': title, 'album' : 'Unknown', 'genre': category, 'artist': artist, 'duration': duration_in_sec(durations[i])})
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)

    xbmcplugin.endOfDirectory(handle, True)

def play_mp3(aid):
    playable_url = "https://api.vk.com/method/audio.getById.json"
    playable_url += "?access_token=cccbeac0c9bf906fc9bf906ff6c991a752cc9bfc9be906709d6d3b8b2d7606d"
    playable_url += "&audios=" + aid

    page = common.fetchPage({"link":  playable_url})
    song = json.loads(page["content"])["response"][0]

    url = song['url']
    title = unescape(song['title'], 'utf-8')
    artist = song['artist']

    item = xbmcgui.ListItem(title)
    item.setInfo('music', {'Title': title, 'Artist': artist})
    xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play(url, item, True)


def play_stream(url, title, category):
    item = xbmcgui.ListItem(path = url)
    item.setInfo('music', {'Title': title, 'Genre': category})

#    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(handle, True, item)


params = get_params()
url  =  None
mode =  None
title =  None
category = None
thumbnail = None
aid = None

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
    aid=params['aid']
except: pass
try:
    thumbnail=urllib.unquote_plus(params['thumbnail'])
except: pass

if mode == None:
    main()
elif mode == 'play_stream':
    play_stream(url, title, category)
elif mode == 'play_mp3':
    play_mp3(aid)
elif mode == 'onlineradio':
    onlineradio(url, category)
elif mode == 'charts':
    charts(url, category)
