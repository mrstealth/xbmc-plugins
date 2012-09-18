#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.4
# -*- coding: utf-8 -*-
# -*- encoding: utf-8 -*-


import xbmcplugin,xbmcgui,xbmcaddon
import os, sys, urllib
import HTMLParser, CommonFunctions
import socket
import simplejson as json

common = CommonFunctions
common.plugin = "plugin.video.iptv5.ts9.ru"

handle = int(sys.argv[1])

Addon = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
addon_icon    = Addon.getAddonInfo('icon')
addon_path    = Addon.getAddonInfo('path')
__settings__ = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')

BASE_URL   = 'http://www.iptv5.ts9.ru/play.htm'

from helpers import *
from category import Category
from channel import Channel

print os.path.join(addon_path, 'resources', 'category.db')
print os.path.join(addon_path, 'resources', 'channel.db')
print "******************+"
category_db = Category('category.db')
channel_db = Channel('channel.db')

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

            #try:
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

def categories(url):
  print "*** list categories"

  categories = category_db.find_all()

  if categories:
    print "FOUND ENTRIES IN DB"
  else:
    print "EMPTY"
    getCategories(url)


def listCategories(url):
  print "*** list categories"



  categories = category_db.find_all()

  if categories:
    print "FOUND ENTRIES IN DB"
  else:
    print "EMPTY"
    getCategories(url)

  #if getCategories(url):
  #  print "SUCCESS"
  #else:
  #  print "ERROR"

def listChannels():
  print "*** list channels"

def play_fav(url):
    item = xbmcgui.ListItem(path = url)
    xbmc.Player().play(url, item)


def play_url(url):
    item = xbmcgui.ListItem(path = url)
    xbmcplugin.setResolvedUrl(handle, True, item)


params = common.getParameters(sys.argv[2])

url=None
mode=None
group=None

try:
    mode=params['mode']
except: pass
try:
    url=urllib.unquote_plus(params['url'])
except: pass
try:
    group=params['group']
except: pass


if mode == 'PLAY':
    play_url(url)
elif mode == 'PLAY2':
    play_fav(url)
elif mode == 'SHOW':
    get_channels_from_db(group)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None:
    categories(BASE_URL)
