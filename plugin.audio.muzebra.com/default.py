#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.4
# -*- coding: utf-8 -*-


import urllib, urllib2, os, sys
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions
from helpers import *

common = CommonFunctions

BASE_URL = 'http://muzebra.com'
handle = int(sys.argv[1])


Addon = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
addon_cache = xbmc.translatePath( Addon.getAddonInfo( "profile" ) )

Language = Addon.getLocalizedString

def main():
    radio = Language(1001)
    uri = construct_url('onlineradio', 'http://muzebra.com/radio/air/', False, False, radio)

    item = xbmcgui.ListItem(radio, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {
        'title': radio,
        'album': BASE_URL,
        'genre': radio,
        'artist': 'muzebra.com'
    })
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    ru_charts = Language(2001)
    uri = construct_url('list_songs', 'http://muzebra.com/charts/', False, False, ru_charts)

    item = xbmcgui.ListItem(ru_charts, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {
        'title': ru_charts,
        'album': BASE_URL,
        'genre': ru_charts,
        'artist': 'muzebra.com'
    })
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    en_charts = Language(2002)
    uri = construct_url('list_songs', 'http://muzebra.com/charts/en/', False, False, en_charts)

    item = xbmcgui.ListItem(en_charts, iconImage = addon_icon, thumbnailImage = addon_icon)
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    ru_artists = Language(3001)
    uri = construct_url('show_alphabet', 'http://muzebra.com/artists/', False, False, 'ru')

    item = xbmcgui.ListItem(ru_artists, iconImage = addon_icon, thumbnailImage = addon_icon)
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    en_artists = Language(3002)
    uri = construct_url('show_alphabet', 'http://muzebra.com/artists/', False, False, 'en')

    item = xbmcgui.ListItem(en_artists, iconImage = addon_icon, thumbnailImage = addon_icon)
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


def showAlphabet(url, category):
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        if category == 'ru':
            letters = common.parseDOM(page["content"], "ul", attrs = { "class":"ru" })
        else:
            letters = common.parseDOM(page["content"], "ul", attrs = { "class":"en" })

        links = common.parseDOM(letters, "a", attrs = { "class":"hash" }, ret="href")
        titles = common.parseDOM(letters, "a")

        if category == 'ru':
            links.insert(1, '/artists/%D0%B0/')
            titles.insert(1, '\xd0\xb0')

        for i, link in enumerate(links):
            # TODO: REFACTORING
            uri = sys.argv[0] + '?mode=list_artists'
            uri += '&url='  + BASE_URL
            uri += '&letter=' + links[i]
            title = titles[i].decode('utf-8').upper()

            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': title})
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    xbmcplugin.endOfDirectory(handle, True)

def listArtists(url, artist):
    url = url + artist
    page = common.fetchPage({"link": url})
#
    if page["status"] == 200:
        artists = common.parseDOM(page["content"], "ul", attrs = { "class":"artists span6" })
        links = common.parseDOM(artists, "a", attrs = { "class":"hash" }, ret="href")
        titles = common.parseDOM(artists, "a")

        for i, link in enumerate(links):
            uri = sys.argv[0] + '?mode=list_songs'
            uri += '&url='  + BASE_URL
            uri += '&artist=' + links[i].split('=')[-1]
            uri += '&category=Artist'

            title = titles[i].decode('utf-8').upper()

            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': title})
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    xbmcplugin.endOfDirectory(handle, True)


def listSongs(url, artist='Unknown', category='Unknown'):
    print url
    print artist
    print category
    if category == 'Artist':
        css_class = "white playlist"
        url = url + '/search/?q=' + artist
        category = artist.decode('utf-8')
    else:
        css_class = "playlist"
        category = category.decode('utf-8')

    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        playlist = common.parseDOM(page["content"], "ul", attrs = { "class": css_class })
        identifiers = common.parseDOM(playlist, "a", attrs = { "class":"info" }, ret="data-aid")

        durations = common.parseDOM(playlist, "div", attrs = { "class":"time" })

        info = common.parseDOM(playlist, "div", attrs = { "class":"title" })
        songs = common.parseDOM(info, "span", attrs = { "class":"name" })
        artists = common.parseDOM(info, "a")

        for i, identifier in enumerate(identifiers):
            # TODO: replace by construect_url
            uri = sys.argv[0] + '?mode=play_mp3'
            uri += '&aid='  + identifier
            uri += '&category=' + artists[i].decode('utf-8')

            song = strip_html(songs[i].decode('utf-8'))
            artist = strip_html(artists[i].decode('utf-8'))
            title = artist + "-" + song

            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {
                'title': title,
                'album' : 'Unknown',
                'genre': 'category',
                'artist': artist,
                'duration': duration_in_sec(durations[i])}
            )
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)

    xbmcplugin.endOfDirectory(handle, True)


def play_stream(url, title, category):
    item = xbmcgui.ListItem(path = url)
    item.setInfo('music', {'Title': title, 'Genre': category})
    xbmcplugin.setResolvedUrl(handle, True, item)

def play_mp3(aid, category):
    song = get_mp3_url(aid)
    url = song['url']
    title = unescape(song['title'], 'utf-8')
    artist = song['artist']

    item = xbmcgui.ListItem(path = url)
    item.setInfo('music', {'Title': title, 'artist' : artist, 'Genre': category})
    xbmcplugin.setResolvedUrl(handle, True, item)

# xbmc.Player() loads faster the next item but can not play next song directly?
def play(url, title, category):
    song = get_mp3_url(aid)

    url = song['url']
    title = unescape(song['title'], 'utf-8')
    artist = song['artist']

    item = xbmcgui.ListItem(title)
    item.setInfo('music', {'Title': title, 'Artist': artist})
    xbmc.Player( xbmc.PLAYER_CORE_MPLAYER ).play(url, item, True)

params = get_params()

url  =  None
mode =  None

title =  None
category = None
artist = None
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
    artist=params['artist']
except: pass
try:
    query=params['query']
except: pass
try:
    artist=params['letter']
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



if mode != None: print "*** MODE " + mode
if mode == None:
    main()
elif mode == 'play_stream':
    play_stream(url, title, category)
elif mode == 'play_mp3':
    # Decide which to use play or play_mp3 ??
    #play(aid, category)
    play_mp3(aid, category)
elif mode == 'onlineradio':
    onlineradio(url, category)
elif mode == 'show_alphabet':
    showAlphabet(url, category)
elif mode == 'list_artists':
    listArtists(url, artist)
elif mode == 'list_songs':
    #getArtist(url, query)
    listSongs(url, artist, category)
