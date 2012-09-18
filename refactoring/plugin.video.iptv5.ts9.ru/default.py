#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.4
# -*- coding: utf-8 -*-


import xbmcplugin,xbmcgui,xbmcaddon
import os, sys, urllib
import HTMLParser, CommonFunctions
import socket
import simplejson as json

common = CommonFunctions
common.plugin = "plugin.video.iptv5.ts9.ru"

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
__language__ = __addon__.getLocalizedString
addon_icon    = __addon__.getAddonInfo('icon')
addon_path    = __addon__.getAddonInfo('path')

BASE_URL   = 'http://www.iptv5.ts9.ru/play.htm'

from helpers import *
from category import Category
from channel import Channel

category_db = Category()
channel_db = Channel()

def getCategories(url):
    print "*** get category from URL"
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")

        for index in range(len(optgroups)):
            optgroup = optgroups[index]
            option = options[optgroups.index(optgroup)]
            name = unescape(optgroup, 'cp1251')

            if category_db.exists(name) == 1:
                print "### CATEGORY already in DB, skip save"
            else:
                print "### Save category %s in DB"%name
                category_db.save(name, index)

            titles = common.parseDOM(option, "option")
            links = common.parseDOM(option, "option", ret="value")

            for i, title in enumerate(titles):
                if channel_db.exists(links[i]) == 0:
                    print "*** Save channel in DB " + unescape(title, 'cp1251')
                    if links[i] != 'http://u.to/rJc0Ag':
                      channel_db.save(unescape(title, 'cp1251'), links[i], index)
                else:
                    print "*** Channel already in DB"

        return True
    else:
        print page["status"]
        return False


def listFavorites():
    label = __language__(1004)

    channels = channel_db.favorites()
    print "channels in fav"
    print channels

    for channel in channels:
      for title,url in channel.items():
        item = xbmcPlayableItem('PLAY', title, url, 'remove')

    xbmcplugin.endOfDirectory(handle, True)


def listCategories(url):    
    xbmcItem('FAVORITES', '', "[COLOR FF00FFF0]" + __language__(1000) + "[/COLOR]")

    categories = category_db.find_all()
    print category_db.checkNeeded(0)
    if not categories:
      getCategories(url)
      categories = category_db.find_all()

    for category in categories:
        for name,category in category.items():
            if int(category) != 8:
                xbmcItem('CHANNELS', '', name, False, category)
            else:
                if __addon__.getSetting('parent_control') == 'false':
                    xbmcItem('CHANNELS', '', name, False, category)

    xbmcplugin.endOfDirectory(handle, True)

def listChannels(category):
    print "*** list channels " + category

    channels = channel_db.find_by_category_id(category)
    print channels

    for channel in channels:
      for title,url in channel.items():
        xbmcPlayableItem('PLAY', title, url, 'add')

    xbmcplugin.endOfDirectory(handle, True)

def play_fav(url):
    item = xbmcgui.ListItem(path = url)
    xbmc.Player().play(url)


def play_url(url):
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(handle, True, item)


params = common.getParameters(sys.argv[2])

url=None
mode=None
category=None

try:
    mode=params['mode']
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    category=params['category']
except: pass


if mode == 'PLAY':
    play_url(url)
elif mode == 'PLAY2':
    play_fav(url)
elif mode == 'CHANNELS':
    listChannels(category)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None:
    listCategories(BASE_URL)
