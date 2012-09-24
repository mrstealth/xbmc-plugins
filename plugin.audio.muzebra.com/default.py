#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.6
# -*- coding: utf-8 -*-


import urllib, urllib2, os, sys, socket
import xbmc, xbmcplugin,xbmcgui,xbmcaddon
import CommonFunctions

from urllib2 import Request, urlopen, URLError, HTTPError
from station import Station
from helpers import *

common = CommonFunctions
stationDB = Station()

BASE_URL = 'http://muzebra.com'
handle = int(sys.argv[1])


Addon = xbmcaddon.Addon(id='plugin.audio.muzebra.com')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
addon_cache = xbmc.translatePath( Addon.getAddonInfo( "profile" ) )

Language = Addon.getLocalizedString

def main():
    search = Language(5000)
    xbmcItem('search', '', search, icon=False, action=False)

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

    moskov = Language(1002)
    uri = construct_url('list_stations', 'http://muzebra.com/radio/msk/', False, False, moskov)

    item = xbmcgui.ListItem(moskov, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {
        'title': moskov,
        'album': BASE_URL,
        'genre': moskov,
        'artist': 'muzebra.com'
    })
    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    piter = Language(1003)
    uri = construct_url('list_stations', 'http://muzebra.com/radio/spb/', False, False, piter)

    item = xbmcgui.ListItem(piter, iconImage = addon_icon, thumbnailImage = addon_icon)
    item.setInfo(type='music', infoLabels = {
        'title': piter,
        'album': BASE_URL,
        'genre': piter,
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

def search():
    query = common.getUserInput("Search for music", "")
    if query != None:
      listSongs(BASE_URL, artist=query.replace (" ", "+"), category='Search')
    else:
      main()

def listFavorites():
    label = __language__(1004)
    stations = stationDB.favorites()

    for station in stations:
        xbmcPlayableItem('PLAY', station[0], station[1], 'remove', station[2])

    xbmcplugin.endOfDirectory(handle, True)

def onlineradio(url, category):
    stations = stationDB.find_all()
    check_enabled = True if Addon.getSetting('availability_check') == 'true' else False

    print "Online radio"
    print  check_enabled

    if not stationDB.recheck() and stations and check_enabled:
      for station in stations:
        for name,url in station.items():
            print name
            uri = sys.argv[0] + '?mode=play_stream'
            uri += '&url='  + urllib.quote_plus(url)
            uri += '&title='  + name.decode('utf-8')
            uri += '&category='  + category.decode('utf-8')

            item = xbmcgui.ListItem(name, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': name, 'genre': category })
            item.setProperty('IsPlayable', 'true')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)
    else:
      page = common.fetchPage({"link": url})

      if page["status"] == 200:
          playlist = common.parseDOM(page["content"], "ul", attrs = { "class":"playlist" })
          links = common.parseDOM(playlist, "a", attrs = { "class":"info" }, ret="data-url")
          titles = common.parseDOM(playlist, "a", attrs = { "class":"info" })

          for i, title in enumerate(titles):
              uri = sys.argv[0] + '?mode=play_stream'
              uri += '&url='  + urllib.quote_plus(links[i])
              uri += '&title='  + titles[i].decode('utf-8')
              uri += '&category='  + category.decode('utf-8')

              if check_enabled:
                if check_url(links[i]):
                    stationDB.save(titles[i], links[i])
                    item = xbmcgui.ListItem(titles[i], iconImage = addon_icon, thumbnailImage = addon_icon)
                    item.setInfo(type='music', infoLabels = {'title': titles[i], 'genre': category })
                    item.setProperty('IsPlayable', 'true')
                    xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)
                else:
                    print "*** skip broken urls"
              else:
                  item = xbmcgui.ListItem(titles[i], iconImage = addon_icon, thumbnailImage = addon_icon)
                  item.setInfo(type='music', infoLabels = {'title': titles[i], 'genre': category })
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
            uri = sys.argv[0] + '?mode=list_artists'
            uri += '&url='  + BASE_URL
            uri += '&letter=' + links[i]
            title = titles[i].decode('utf-8').upper()

            item = xbmcgui.ListItem(title, iconImage = addon_icon, thumbnailImage = addon_icon)
            item.setInfo(type='music', infoLabels = {'title': title})
            item.setProperty('IsPlayable', 'false')
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    xbmcplugin.endOfDirectory(handle, True)


def listStations(url, category):
    print "*** listStations " + url
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        print page
        stations = common.parseDOM(page["content"], "ul", attrs = { "class":"stations" })
        thumb_div = common.parseDOM(stations, "div", attrs = { "class":"thumb" })
        thumbs = common.parseDOM(thumb_div, "img", ret="src")

        name_div = common.parseDOM(stations, "div", attrs = { "class":"name" })
        links = common.parseDOM(name_div, "a", attrs = { "class":"hash" }, ret="href")
        titles = common.parseDOM(name_div, "a")
        
        for i, title in enumerate(titles):
            uri = sys.argv[0] + '?mode=list_songs'
            uri += '&url='  + urllib.quote_plus(BASE_URL+links[i])
            uri += '&title='  + titles[i].decode('utf-8')
            uri += '&category='  + category.decode('utf-8')

            thumb = BASE_URL+thumbs[i]

            item = xbmcgui.ListItem(titles[i], thumbnailImage = thumb)
            item.setInfo(type='music', infoLabels = {'title': titles[i], 'genre': category })
            xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=True)

    xbmcplugin.endOfDirectory(handle, True)


def listArtists(url, artist):
    url = url + artist
    page = common.fetchPage({"link": url})

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
    if category == 'Artist' or category == 'Search':
        url = BASE_URL + '/search/?q=' + artist

    if category == 'Search':
        values = {'_':'1348127480611', '_pjax':'true'}

        try:
            response = urlopen(Request(url, urllib.urlencode(values)))
        except URLError, e:
            if hasattr(e, 'reason'):
                print 'We failed to reach a server' + ', reason: ', e.reason
            elif hasattr(e, 'code'):
                print 'The server couldn\'t fulfill the request,' + ' error code: ', e.code
        else:
            getListItems(response.read(), url, artist, category)
    else:
      page = common.fetchPage({"link": url})['content']
      getListItems(page, url, artist, category)

    xbmcplugin.endOfDirectory(handle, True)

def getListItems(page, url, artist, category):
    if category == 'Artist' or category == 'Search':
        css_class = "white playlist"
        category = artist.decode('utf-8')
    else:
        css_class = "playlist"
        category = category.decode('utf-8')

    playlist = common.parseDOM(page, "ul", attrs = { "class": css_class })
    identifiers = common.parseDOM(playlist, "a", attrs = { "class":"info" }, ret="data-aid")

    durations = common.parseDOM(playlist, "div", attrs = { "class":"time" })
    info = common.parseDOM(playlist, "div", attrs = { "class":"title" })
    songs = common.parseDOM(info, "span", attrs = { "class":"name" })
    artists = common.parseDOM(info, "a")

    for i, identifier in enumerate(identifiers):
        title = strip_html(songs[i].decode('utf-8'))
        artist = strip_html(artists[i]).decode('utf-8')
        song = artist + '-' + title

        uri = sys.argv[0] + '?mode=play_mp3'
        uri += '&aid=%s'%identifier

        item = xbmcgui.ListItem(song, iconImage = addon_icon, thumbnailImage = addon_icon)
        item.setInfo(type='music', infoLabels = {
            'title': title,
            'artist': artist,
            'duration': duration_in_sec(durations[i])}
        )
        item.setProperty('IsPlayable', 'true')
        xbmcplugin.addDirectoryItem(handle, uri, item, isFolder=False)

def play_mp3(aid):
    url = get_mp3_url(aid)['url']

    if url:
      item = xbmcgui.ListItem(path = url)
      item.setProperty('mimetype', 'audio/mpeg')
      xbmcplugin.setResolvedUrl(handle, True, item)
    else:
      xbmcplugin.endOfDirectory(handle, True)

def play(url, title, category):
    item = xbmcgui.ListItem(path = url)
    #item.setInfo(type='music', infoLabels = {'title': title, 'artist': title})
    #item.setProperty('mimetype', 'audio/mpeg')
    xbmcplugin.setResolvedUrl(handle, True, item)


params = common.getParameters(sys.argv[2])

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


if mode == None:
    main()
elif mode == 'play_stream':
    #play_stream(url, title, category)
    play(url, title, category)
elif mode == 'play_mp3':
    play_mp3(aid)
elif mode == 'search':
    search()
elif mode == 'onlineradio':
    onlineradio(url, category)
elif mode == 'list_stations':
    listStations(url, category)
elif mode == 'show_alphabet':
    showAlphabet(url, category)
elif mode == 'list_artists':
    listArtists(url, artist)
elif mode == 'list_songs':
    listSongs(url, artist, category)
