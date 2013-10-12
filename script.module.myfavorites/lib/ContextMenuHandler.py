#!/usr/bin/python
# Writer (c) 2012, MrStealth
# License: GPLv3

import urllib

import xbmc
import xbmcaddon

import XbmcHelpers
common = XbmcHelpers

icon = xbmcaddon.Addon('script.module.favorites').getAddonInfo('icon')
language = xbmcaddon.Addon('script.module.favorites').getLocalizedString

params = dict([(k, urllib.unquote_plus(v)) for k,v in common.getParameters(sys.argv[1]).items()])

from MyFavorites import MyFavoritesDB
database = MyFavoritesDB(params['plugin'])

if params['action'] == "add":
    xbmc.executebuiltin('XBMC.Notification(My Favorites, Item added to "My Favorites", 3000, %s) % icon')
    database.save(params['title'], params['url'], params['image'], params['playable'] == 'True')
else:
    xbmc.executebuiltin('XBMC.Notification(My Favorites, Item removed from "My Favorites", 3000, %s) % icon')
    database.remove(params['title'])
    xbmc.executebuiltin("Container.Refresh")
