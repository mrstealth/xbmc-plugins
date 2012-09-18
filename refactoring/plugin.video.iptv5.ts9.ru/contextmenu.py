#!/usr/bin/python
# Writer (c) 2012, MrStealth
# -*- coding: utf-8 -*-

import xbmc,xbmcaddon
import simplejson as json
from channel import Channel

__addon__    = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
_addon_icon    =__addon__.getAddonInfo('icon')

channel_db = Channel()

def addFavorite(url, name):
    channel = channel_db.addToFav(url)

def removeFavorite(url, name):
    channel = channel_db.removeFromFav(url)

# ***** MAIN *****
args = sys.argv[1].split("|")

if(args[0] == "add"):
    addFavorite(args[1], args[2])

    title = "[COLOR FF00FF00]" + "SUCCESS" + "[/COLOR]"
    message = "Item successfully added to your favorites"
    xbmc.executebuiltin("XBMC.Notification("+ title +","+ message +","+ str(3*1000) +","+ _addon_icon +")")

elif(args[0] == "remove"):
    removeFavorite(args[1], args[2])

    title = "[COLOR FF00FF00]" + "SUCCESS" + "[/COLOR]"
    message = "Item successfully removed from your favorites"

    xbmc.executebuiltin("XBMC.Notification("+ title +","+ message +","+ str(3*1000) +","+ _addon_icon +")")
    xbmc.executebuiltin("Container.Refresh")

else:
    print "INVALID ARG PASSED IN (sys.argv[1]=" + sys.argv[1]
