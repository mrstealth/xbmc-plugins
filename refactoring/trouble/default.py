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
    # add reset database to settings
    # and set it again
        
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")

        #progress = xbmcgui.DialogProgress()
        #progress.create('Check stream availability', 'this process might take several minutes')
            
        for index in range(len(optgroups)):
            optgroup = optgroups[index]
            option = options[optgroups.index(optgroup)]
            name = unescape(optgroup, 'cp1251')

            #progress.update((index*12.5), 'Category' + str(index) + '/', str(len(optgroups)))
            
            if category_db.exists(name) == 1:
                print "### CATEGORY already in DB, skip save"
            else:
                print "### Save category %s in DB"%name
                category_db.save(name, index, True)

            titles = common.parseDOM(option, "option")
            links = common.parseDOM(option, "option", ret="value")

            for i, title in enumerate(titles):
                if links[i] != 'http://u.to/rJc0Ag':
                    print "save channel " + unescape(title, 'cp1251')
                    channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)


        #progress.close()
        return True
    else:
        print page["status"]
        #progress.close()
        return False


def getChannels(name, index):
    print "*** get channels from URL for " + name + " and id " + index 
    page = common.fetchPage({"link": BASE_URL})
    index = int(index)

    if page["status"] == 200:
        select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
        optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
        options = common.parseDOM(select, "optgroup")
        
        print "### Save category %s in DB and update timestamp "%name
        category_db.save(name, index, False)

        for i in range(len(optgroups)):
            optgroup = optgroups[i]
            if i == index: 
                option = options[optgroups.index(optgroup)]
                titles = common.parseDOM(option, "option")
                links = common.parseDOM(option, "option", ret="value")
        
                for i, title in enumerate(titles):
                    if links[i] != 'http://u.to/rJc0Ag':
                        if __addon__.getSetting('availability_check') == 'true':
                            if available(links[i]):
                                print "*** save channel: " + unescape(title, 'cp1251')
                                channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
                            else:
                                print "*** mark as unavailable: " + unescape(title, 'cp1251')
                                channel_db.save(unescape(title, 'cp1251'), links[i], index, 1)
                        else:
                            print "*** save channel without availability check: " + unescape(title, 'cp1251')
                            channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
                            
                
        return True
    else:
        return False

def listFavorites():
    label = __language__(1004)

    channels = channel_db.favorites()
    print channels

    for channel in channels:
      for title,url in channel.items():
        item = xbmcPlayableItem('PLAY', title, url, 'remove')

    xbmcplugin.endOfDirectory(handle, True)


def listCategories(url):    
    xbmcItem('FAVORITES', '', "[COLOR FF00FFF0]" + __language__(1000) + "[/COLOR]")

    categories = category_db.find_all()
    if not categories:
        getCategories(url) # initial import
        categories = category_db.find_all()

    for category in categories:
        print category

        for name,optgroupid in category.items():
            if int(optgroupid) != 8:
                xbmcItem('CHANNELS', '', name, False, optgroupid)
            else:
                print optgroupid
                if __addon__.getSetting('parent_control') == 'false':
                    xbmcItem('CHANNELS', '', name, False, optgroupid)

    xbmcplugin.endOfDirectory(handle, True)

def listChannels(name, optgroupid):
    print "*** list channels " + name + ' '+ optgroupid

    outdated = category_db.find_outdated()
    print "*** detect outdated categories "
    print outdated
    #outdated = [1,2]

    if optgroupid in outdated:
        print "*** check " + name
        getChannels(name, optgroupid)
    
    channels = channel_db.find_by_category_id(optgroupid)
 
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
    title=params['title']
except: pass
try:
    category=params['category']
except: pass


if mode == 'PLAY':
    play_url(url)
elif mode == 'PLAY2':
    play_fav(url)
elif mode == 'CHANNELS':
    listChannels(title, category)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None:
    listCategories(BASE_URL)
