#!/usr/bin/python
# Writer (c) 2012, MrStealth
# -*- coding: utf-8 -*-

import xbmc,xbmcaddon
import simplejson as json

__addon__    = xbmcaddon.Addon(id='plugin.video.iptv5.ts9.ru')
_addon_icon    =__addon__.getAddonInfo('icon')

def addFavorite(url, name):
    favorites = {} if len(__addon__.getSetting('favorites')) == 0 else json.loads(__addon__.getSetting('favorites'))    
    favorites[url] = name

    # save json string in settings.xml
    __addon__.setSetting('favorites', json.dumps(favorites))

def removeFavorite(url, name):
    if len(__addon__.getSetting('favorites')) != 0:
        favorites = json.loads(__addon__.getSetting('favorites'))    
        del favorites[url]
    
        # save json string in settings.xml
        __addon__.setSetting('favorites', json.dumps(favorites))
    
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