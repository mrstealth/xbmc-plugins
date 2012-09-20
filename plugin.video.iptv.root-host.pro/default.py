#!/usr/bin/python
# Writer (c) 2012, MrStealth
# Rev. 1.0.0
# -*- coding: utf-8 -*-


import xbmcplugin,xbmcgui,xbmcaddon
import os, sys, urllib
import HTMLParser, CommonFunctions
import urllib2, socket, urlparse
import simplejson as json

common = CommonFunctions
common.plugin = "plugin.video.iptv.root-host.pro"
common.dbg = True # Default
common.dbglevel = 0 # Default

handle = int(sys.argv[1])

__addon__ = xbmcaddon.Addon(id='plugin.video.iptv.root-host.pro')
__language__ = __addon__.getLocalizedString
addon_icon    = __addon__.getAddonInfo('icon')
addon_path    = __addon__.getAddonInfo('path')

BASE_URL   = 'http://iptv.root-host.pro'

from helpers import *
from category import Category
from channel import Channel

category_db = Category()
channel_db = Channel()


# <td width=10%>1</td>
# <td width=10%> <img src="http://www.abload.de/img/stsoj7jf.png" height="30" width="30"></td>
# <td><a href="index.php?name=STS&logo=http://www.abload.de/img/stsoj7jf.png&nummer=1&kat=Standard">STS</a></td>
# <td><a href="index.php?show=1&link=tvkanal.php?kanal=1">show</a></td><td>Standard.</td>


def getCategories(url):
    url=urllib.unquote_plus(url)
    page = common.fetchPage({"link": url})

    if page["status"] == 200:
        table = common.parseDOM(page["content"], "tr")        
        hrefs = []
        
        for i, tr in enumerate(table):
            td = common.parseDOM(tr, "td")
            url = common.parseDOM(td[0], "a", ret="href")[0]
            hrefs.append(common.getParameters(url).values())
        
        for params in hrefs:
            channel_db.save(params[0], params[1], params[2], params[3])
            xbmcPlayableItem('play', params[0], params[1], params[2], params[3])

        xbmcplugin.endOfDirectory(handle, True)
#         select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
#         optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
#         options = common.parseDOM(select, "optgroup")
#         try:
#             for index in range(len(optgroups)):
#                 optgroup = optgroups[index]
#                 option = options[optgroups.index(optgroup)]
#                 name = unescape(optgroup, 'cp1251')
# 
#                 if category_db.exists(name) == 1:
#                     print "### CATEGORY already in DB, skip save"
#                 else:
#                     print "### Save category %s in DB"%name
#                     category_db.save(name, index, True)
# 
#                 titles = common.parseDOM(option, "option")
#                 links = common.parseDOM(option, "option", ret="value")
# 
#                 for i, title in enumerate(titles):
#                     if links[i] != 'http://u.to/rJc0Ag':
#                         print "save channel " + unescape(title, 'cp1251')
#                         channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
#             return True
# 
#         except:
#            print "Unexpected error:", sys.exc_info()[0]
#            print "Unexpected error:", sys.exc_info()[1]
#            print "Unexpected error:", sys.exc_info()[2]


    else:
        print page["status"]
        return False


def getChannels(name, index):
    print "*** get channels from URL for " + name + " and id " + index
    page = common.fetchPage({"link": BASE_URL})
    index = int(index)

    if page["status"] == 200:

#         select = common.parseDOM(page["content"], "select", attrs = { "id":"ch" })
#         optgroups = common.parseDOM(select, "optgroup", ret="label")[0:-1]
#         options = common.parseDOM(select, "optgroup")
# 
#         print "### Save category %s in DB and update timestamp "%name
#         category_db.save(name, index, False)
# 
#         for i in range(len(optgroups)):
#             optgroup = optgroups[i]
#             if i == index:
#                 option = options[optgroups.index(optgroup)]
#                 titles = common.parseDOM(option, "option")
#                 links = common.parseDOM(option, "option", ret="value")
# 
#                 for i, title in enumerate(titles):
#                     if links[i] != 'http://u.to/rJc0Ag':
#                         if __addon__.getSetting('availability_check') == 'true':
#                             if check_url(links[i]):
#                                 print "*** save channel: " + unescape(title, 'cp1251')
#                                 channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
#                             else:
#                                 print "*** mark as unavailable: " + unescape(title, 'cp1251')
#                                 channel_db.save(unescape(title, 'cp1251'), links[i], index, 1)
#                         else:
#                             print "*** save channel without availability check: " + unescape(title, 'cp1251')
#                             channel_db.save(unescape(title, 'cp1251'), links[i], index, 0)
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
    xbmcItem('FAVORITES', '', "[COLOR FF00FFF0]" + __language__(1000).encode('utf-8') + "[/COLOR]")

    print channel_db.get_categories()
    
    for category in channel_db.get_categories():
        xbmcItem('CHANNELS', '', category, category)
#     categories = category_db.find_all()
#     if not categories:
#         getCategories(url) # initial import
#         categories = category_db.find_all()
# 
#     for category in categories:
#         print category
# 
#         for name,optgroupid in category.items():
#             if int(optgroupid) != 8:
#                 xbmcItem('CHANNELS', '', name, False, optgroupid)
#             else:
#                 print optgroupid
#                 if __addon__.getSetting('parent_control') == 'false':
#                     xbmcItem('CHANNELS', '', name, False, optgroupid)

    xbmcplugin.endOfDirectory(handle, True)

def listChannels(name, category):
    channels = channel_db.find_by_category_name(category)
    
    print channels
    for channel in channels:
        print len(channel)
        xbmcPlayableItem('play', channel[0], channel[1], channel[2], channel[3])
#     print "*** list channels " + name + ' '+ optgroupid
# 
#     outdated = category_db.find_outdated()
#     print "*** detect outdated categories "
#     print outdated
#     #outdated = [1,2]
# 
#     if optgroupid in outdated:
#         print "*** check " + name
#         getChannels(name, optgroupid)
# 
#     channels = channel_db.find_by_category_id(optgroupid)
# 
#     for channel in channels:
#       for title,url in channel.items():
#         xbmcPlayableItem('PLAY', title, url, 'add')

    xbmcplugin.endOfDirectory(handle, True)

def play(url, title):
    host = BASE_URL + '/tvkanal.php?kanal=%s'%url

    
    stream = check_url(host)
    if stream:
        listitem = xbmcgui.ListItem(label=title, iconImage=addon_icon, thumbnailImage=addon_icon, path=stream['url'])
        listitem.setProperty('mimetype', stream['mimetype'])
        xbmcplugin.setResolvedUrl(handle=int(sys.argv[1]), succeeded=True, listitem=listitem)
    else:
        title = "Unplayble channel " + title
        message = "Mark as broken in DB and recheck in 2 hours"
        xbmc.executebuiltin("XBMC.Notification("+ title +","+ message +","+ str(3*1000) +","+ addon_icon +")")

params = common.getParameters(sys.argv[2])

mode=None
image=None
url=None
title=None
category=None

try:
    mode=params['mode']
except: pass
try:
    image=params['image']
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

if mode == 'play':
    play(url, title)
elif mode == 'CHANNELS':
    listChannels(title, category)
elif mode == 'FAVORITES':
    listFavorites();
elif mode == None:
    listCategories(BASE_URL)